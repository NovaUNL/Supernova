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
    content = serializers.CharField()


class SectionRelationSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='section.id')
    name = serializers.CharField(source='section.name')
    index = serializers.IntegerField()


class TopicSectionsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sections = SectionRelationSerializer(source='sectiontopic_set', many=True)

class ClassSectionsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sections = SectionRelationSerializer(source='classsection_set', many=True)