class ActionDependentSerializerMixin(object):
    '''
    Supports differentiating serializers across actions
    '''

    def get_serializer_class(self):
            return self.serializers.get(self.action, self.serializers['default'])


class FieldLimitableSerializerMixin(object):
    '''
    Supports limiting the return fields via the specified include and exclude
    query parameters from a request by passing the data into the serializer via
    the serializer context. Only works with PrefetchedSerializer descendants
    '''

    def get_serializer_context(self):
        context = super(FieldLimitableSerializerMixin, self).get_serializer_context()

        include_param_name = "include"
        exclude_param_name = "exclude"

        # Check query params for "include", which are included fields
        if include_param_name in self.request.query_params:
            context = {**context, "override_fields": self.request.query_params.get(include_param_name).split(',')}
        # Check query params for "exclude", which are excluded fields
        if exclude_param_name in self.request.query_params:
            context = {**context, "override_exclude": self.request.query_params.get(exclude_param_name).split(',')}

        return context
