from rest_framework import serializers


class NewsMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    summary = serializers.CharField()
    datetime = serializers.DateTimeField()


class NewsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    summary = serializers.CharField()
    content = serializers.CharField()
    datetime = serializers.DateTimeField()
    # author = TODO
