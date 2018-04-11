from rest_framework import serializers


class GroupMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


class GroupTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    group_set = GroupMinimalSerializer(many=True)
