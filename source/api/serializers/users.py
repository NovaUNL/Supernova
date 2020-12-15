from rest_framework import serializers

from api.serializers.college import StudentSerializer
from users.models import ExternalPage


class ProfileMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    nickname = serializers.CharField()


class ProfileDetailedSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    name = serializers.CharField()
    students = StudentSerializer(many=True)


class ExternalPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalPage
        fields = ['id', 'platform', 'url', 'name']
