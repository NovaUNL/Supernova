from rest_framework import serializers

from api.serializers.college import StudentSerializer


class ProfileMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    nickname = serializers.CharField()


class ProfileDetailedSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    name = serializers.CharField()
    student_set = StudentSerializer(many=True)
