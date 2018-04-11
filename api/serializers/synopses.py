from rest_framework import serializers


class TopicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class SubareaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    topics = TopicSerializer(many=True)


class AreaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    subareas = SubareaSerializer(many=True)


class SectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class TopicSectionsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    section = SectionSerializer(many=True)
