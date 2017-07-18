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

        # Create our nested serializers
        if hasattr(self.Meta, "nested"):
            for name, nested in self.Meta.nested.items():
                # Get the nested serializer's kwargs
                kwargs = nested.get("kwargs", {})

                # If our serializer field name is not the same as the source, specify it
                if nested.get("field", False) and name != nested["field"]:
                    kwargs["source"] = nested["field"]
                    self.fields.pop(nested["field"])

                self.fields[name] = nested["class"](**kwargs)

        # Iterate over our fields and modify the list as necessary
        for field in list(self.fields.keys()):
            # Ignore any fields that begin with _
            if field[0] == "_":
                self.fields.pop(field)
            # If we have overriden fields, remove fields not present in the requested list
            elif len(override_fields) > 0 and field not in override_fields:
                self.fields.pop(field)
            # If we have overriden exclusions, remove fields present in the exclusion list
            elif field in override_exclude:
                self.fields.pop(field)

    @classmethod
    def prefetch_model(cls, model, queryset, prefix=""):
        '''
        This method sets up prefetch and selected related statements when applicable
        for foreign key relationships.

        It iterates over all fields in the object, if the field is (1) a related
        field type, and (2) not a reverse lookup, it pre-fetches that field, and
        all sub-fields
        '''
        related_field_types = ["OneToOneField", "ManyToManyField", "ForeignKey"]
        for field in model._meta.get_fields():
            if field.get_internal_type() in related_field_types and not hasattr(field, 'related_name'):
                queryset = queryset.prefetch_related(f"{prefix}{field.name}")
                if field.related_model != model:
                    queryset = cls.prefetch_model(field.related_model, queryset, prefix=f"{prefix}{field.name}{LOOKUP_SEP}")

        return queryset
