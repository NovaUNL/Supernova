from rest_framework import serializers


# Serializes a reference to a section (its id and name).
class SectionReferenceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()


# Serializes a section source
class SectionSourceSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.URLField()


class SectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content_ck = serializers.CharField()
    sources = SectionSourceSerializer(many=True)
    requirements = SectionReferenceSerializer(many=True)


class SubareaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sections = SectionSerializer(many=True)


class AreaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subareas = SubareaSerializer(many=True)


class SectionRelationSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='section.id')
    title = serializers.CharField(source='section.title')
    index = serializers.IntegerField()


class SubSectionsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    children = SectionRelationSerializer(source='children_intermediary', many=True)
    # children = serializers.IntegerField(source='children_intermediary', many=True)


class ClassSectionsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sections = SectionRelationSerializer(source='synopsis_sections', many=True)
