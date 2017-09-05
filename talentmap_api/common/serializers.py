from rest_framework import serializers
from django.db.models.constants import LOOKUP_SEP


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
            override_fields += self.context.get("override_fields")
        if "override_exclude" in self.context:
            override_exclude += self.context.get("override_exclude")

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
                self.fields[name] = nested["class"](**kwargs)

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
    def prefetch_model(cls, model, queryset, prefix="", visited=None):
        '''
        This method sets up prefetch and selected related statements when applicable
        for foreign key relationships.

        It iterates over all fields in the object, if the field is (1) a related
        field type, and (2) not a reverse lookup, it pre-fetches that field, and
        all sub-fields
        '''
        related_field_types = ["OneToOneField", "ManyToManyField", "ForeignKey"]

        # Don't prefetch already prefetched items
        if not visited:
            visited = []
        elif model in visited:
            return queryset
        visited.append(model)

        for field in model._meta.get_fields():
            if field.get_internal_type() in related_field_types and not hasattr(field, 'related_name'):
                queryset = queryset.prefetch_related(f"{prefix}{field.name}")
                if field.related_model != model:
                    queryset = cls.prefetch_model(field.related_model, queryset, prefix=f"{prefix}{field.name}{LOOKUP_SEP}", visited=visited)

        return queryset
