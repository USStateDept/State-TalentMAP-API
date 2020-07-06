from pydoc import locate

from rest_framework import serializers
from django.db.models.constants import LOOKUP_SEP

from talentmap_api.common.models import StaticRepresentationModel


class StaticRepresentationField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, StaticRepresentationModel):
            return value._string_representation
        else:
            return str(value)


class PrefetchedSerializer(serializers.ModelSerializer):
    '''
    This class extends the base model serializer and provides built-in related
    field prefetching to resolve N+1 issues on nested serializers.

    To specify a nested serializer, specify a serializer in the "nested" Meta
    field thusly:
    "serializer_field_name": {
        "class": SomeSerializer,
        "field": "SourceDataField",
        "kwargs": {
            "override_fields": [] // List of fields to _only_ include
            "override_exclude": []
            "read_only": True,
            "many": True
        }

    }
    '''

    def __init__(self, *args, **kwargs):
        override_fields = kwargs.pop("override_fields", [])
        override_exclude = kwargs.pop("override_exclude", [])

        # Initializer our parent serializer
        super(PrefetchedSerializer, self).__init__(*args, **kwargs)

        # Check the context for overrides from query params
        if "override_fields" in self.context:
            override_fields += self.context.pop("override_fields")
        if "override_exclude" in self.context:
            override_exclude += self.context.pop("override_exclude")

        override_fields = self.correct_include_hierarchy(override_fields)

        # Create our nested serializers
        if hasattr(self.Meta, "nested"):
            for name, nested in self.Meta.nested.items():
                # Get the nested serializer's kwargs
                kwargs = dict(nested.get("kwargs", {}))

                # If our serializer field name is not the same as the source, specify it
                if nested.get("field", False) and name != nested["field"]:
                    kwargs["source"] = nested["field"]
                    self.fields.pop(nested["field"])

                self.parse_child_overrides(override_fields, override_exclude, name, nested, kwargs)

                # Inherit our current context
                kwargs["context"] = self.context

                # If our class is specified as a string, import it
                if isinstance(nested["class"], str):
                    nested["class"] = locate(nested["class"])

                self.fields[name] = nested["class"](**kwargs)

        # Get our list of writable fields, if it exists
        # Allow either list, tuple, or string to conform with similar other DRF behaviors
        writable_fields = self.get_writable_fields()

        # Iterate over our fields and modify the list as necessary
        for field in list(self.fields.keys()):
            # Ignore any fields that begin with _
            if field[0] == "_":
                self.fields.pop(field)
            # If we have overridden fields, remove fields not present in the requested list
            elif override_fields and field not in override_fields:
                self.fields.pop(field)
            # If we have overridden exclusions, remove fields present in the exclusion list
            elif field in override_exclude:
                self.fields.pop(field)
            # Deny write access to all fields unless explicitly stated
            elif field not in writable_fields:
                self.fields[field].read_only = True

    def get_writable_fields(self):
        writable_fields = []
        if hasattr(self.Meta, "writable_fields"):
            if isinstance(self.Meta.writable_fields, list):
                writable_fields = self.Meta.writable_fields
            elif isinstance(self.Meta.writable_fields, tuple):
                writable_fields = list(self.Meta.writable_fields)
            elif isinstance(self.Meta.writable_fields, str):
                writable_fields = [self.Meta.writable_fields]

        return writable_fields

    def validate(self, data):
        """
        Object level validation, all descendants should call this via Super()
        if it is overriden.

        Validates that only fields available in writable_fields are being written
        """
        # Data may be stripped of invalid fields before it gets here, check
        if len(data.keys()) == 0:
            raise serializers.ValidationError("Invalid data")

        # Get a list of writable fields
        writable_fields = self.get_writable_fields()
        invalid_fields = [x for x in data.keys() if x not in writable_fields]
        if len(invalid_fields) > 0:
            raise serializers.ValidationError(f"The following fields are not writable: {', '.join(invalid_fields)}")
        return data

    def get_representation(self, obj):
        '''
        Allows children to add `representation = serializers.SerializerMethodField()` to add
        their string representation to their own serializer
        '''
        if isinstance(obj, StaticRepresentationModel):
            return obj._string_representation
        else:
            return str(obj)

    @classmethod
    def correct_include_hierarchy(cls, override_fields):
        '''
        This method ensures that the list of override fields includes any items' parents
        For example:
            ["description__id"] would not render any data, as it is excluding the parent, "description"
        This method fixes this issue by ensuring all parents are included

        Args:
            override_fields (list) - List of overridden fields to include

        Returns:
            list - List of overridden fields, including first level parents
        '''

        extra_fields = [x.split(LOOKUP_SEP)[0] for x in override_fields if len(x.split(LOOKUP_SEP)) > 1]
        return override_fields + extra_fields

    @classmethod
    def parse_child_overrides(cls, override_fields, override_exclude, name, nested, child_kwargs):
        '''
        This method populates a dictionary object with appropriate cascaded child serializers

        Args:
            override_fields (list) - List of overridden fields from the parent
            override_exclude (list) - List of overridden field exclusions from the parent
            name (string) - The field name of the child
            nested (Object) - The nested object of the child
            child_kwargs (Object) - The kwarg object for the child, modified in place
        '''
        # If our parent serializer has field limitations on the child, pass them down
        for pair in [(override_fields, "override_fields"), (override_exclude, "override_exclude")]:
            overrides = pair[0]
            child_overrides = []

            for field in overrides:
                split_field = field.split(LOOKUP_SEP)
                # Skip this field if we don't have a nested field
                if len(split_field) == 1:
                    continue
                if split_field[0] == name or split_field[0] == nested.get("field", ""):
                    child_overrides.append(LOOKUP_SEP.join(split_field[1:]))

            # If we have child overrides, attach them to the child's kwargs
            if child_overrides:
                child_kwargs[pair[1]] = child_overrides

    @classmethod
    def prefetch_model(cls, model, queryset, prefix="", parent_method=None, visited=None):
        '''
        This method sets up prefetch and selected related statements when applicable
        for foreign key relationships.

        It iterates over all fields in the object, if the field is (1) a related
        field type, and (2) not a reverse lookup, it pre-fetches that field, and
        all sub-fields
        '''
        select_related_field_types = ["OneToOneField", "ForeignKey"]
        prefetch_field_types = ["ManyToManyField"]

        # Don't prefetch already prefetched items
        if not visited:
            visited = []
        elif model in visited:
            return queryset
        visited.append(model)

        # Only prefetch serialized fields
        serialized_field_names = cls().fields.keys()
        fields = [x for x in model._meta.get_fields() if x.name in serialized_field_names]

        for field in fields:
            internal_type = field.get_internal_type()
            method = None
            # If this attribute is present, we are fetching a reverse-lookup, and need to use prefetch_related
            if hasattr(field, 'related_name'):
                method = "prefetch_related"
            # If we're a forward-lookup, we need to check the related field types
            # For OneToOne and ForeignKey, use select_related
            elif internal_type in select_related_field_types:
                method = "select_related"
            # Use prefetch_related for "many" relationships
            elif internal_type in prefetch_field_types:
                method = "prefetch_related"
            # Otherwise, we're just a base field and can skip
            else:
                continue

            # If we're a n-level nesting (n>1) we need to prefetch_related if at some point
            # in the relationship chain we prefetch related
            if parent_method == "prefetch_related":
                method = parent_method

            # Call the appropriate prefetch method
            queryset = getattr(queryset, method)(f"{prefix}{field.name}")
            # If we have a related model to step into, do so
            if field.related_model != model:
                # If our serializer has a meta class (it should if it is a PrefetchedSerializer)
                if hasattr(cls.Meta, "nested"):
                    nested_serializer_class = cls.Meta.nested.get(field.name, None)
                    # If we have a nested serializer class, use it to prefetch the next level of fields
                    if nested_serializer_class:
                        queryset = nested_serializer_class.get("class").prefetch_model(field.related_model, queryset, parent_method=method, prefix=f"{prefix}{field.name}{LOOKUP_SEP}", visited=visited)

        return queryset
