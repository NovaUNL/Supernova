from rest_framework import serializers

from users.models import ExternalPage


class ProfileMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    nickname = serializers.CharField()


class ProfileDetailedSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nickname = serializers.CharField()
    name = serializers.CharField()
    # TODO complete


class ExternalPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalPage
        fields = ['id', 'platform', 'url', 'name']
