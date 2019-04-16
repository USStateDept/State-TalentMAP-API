from rest_framework import serializers

class FSBidSerializer(serializers.Serializer):
  id = serializers.IntegerField(read_only=True)
  

