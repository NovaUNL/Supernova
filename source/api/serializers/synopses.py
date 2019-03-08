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


# Serializes a section source
class SectionSourceSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.URLField()


# Serializes a reference to a section (its id and name).
class SectionReferenceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class SectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    content = serializers.CharField()
    sources = SectionSourceSerializer(many=True)
    requirements = SectionReferenceSerializer(many=True)


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
