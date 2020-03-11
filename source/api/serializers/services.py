from rest_framework import serializers

from api.serializers.college import BuildingSerializer


class ServiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=True)
    opening = serializers.IntegerField(required=False)
    lunch_start = serializers.IntegerField(required=False)
    lunch_end = serializers.IntegerField(required=False)
    closing = serializers.IntegerField(required=False)


class ServiceWithBuildingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=True)
    opening = serializers.IntegerField(required=False)
    lunch_start = serializers.IntegerField(required=False)
    lunch_end = serializers.IntegerField(required=False)
    closing = serializers.IntegerField(required=False)
    building = BuildingSerializer()