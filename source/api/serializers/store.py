from rest_framework import serializers

from api.serializers.groups import GroupMinimalSerializer


class StoreItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.IntegerField()
    stock = serializers.IntegerField()
    seller = GroupMinimalSerializer()
