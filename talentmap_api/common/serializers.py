from rest_framework import serializers


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
            "read_only": True,
            "many": True
        }

    }
    '''
    def __init__(self, *args, **kwargs):
        # Initializer our parent serializer
        super(PrefetchedSerializer, self).__init__(*args, **kwargs)

        # Create our nested serializers
        if hasattr(self.Meta, "nested"):
            for name, nested in self.Meta.nested.items():
                # Get the nested serializer's kwargs
                kwargs = nested.get("kwargs", {})

                # If our serializer field name is not the same as the source, specify it
                if name != nested["field"]:
                    kwargs["source"] = nested["field"]

                self.fields[name] = nested["class"](**kwargs)

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
                queryset = queryset.prefetch_related("{}{}".format(prefix, field.name))
                queryset = cls.prefetch_model(field.related_model, queryset, prefix="{}{}__".format(prefix, field.name))

        return queryset
