from rest_framework import serializers

from api.serializers.college import StudentSerializer
from users.models import SocialNetworkAccount


class ProfileMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    nickname = serializers.CharField()


class ProfileDetailedSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    name = serializers.CharField()
    student_set = StudentSerializer(many=True)


class SocialNetworksSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialNetworkAccount
        fields = ['network', 'profile']
