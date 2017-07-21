class ActionDependentSerializerMixin(object):
    '''
    Supports differentiating serializers across actions
    '''

    def get_serializer_class(self):
            return self.serializers.get(self.action, self.serializers['default'])
