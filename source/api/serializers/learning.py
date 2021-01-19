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
    id = serializers.IntegerField(source='activity_id')
    title = serializers.CharField()
    content = serializers.CharField(source='content_md')
    sources = SectionSourceSerializer(many=True)
    requirements = SectionReferenceSerializer(many=True)
    url = serializers.CharField(source='get_absolute_url')


class SectionPreviewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField(source='content_md')
    url = serializers.CharField(source='get_absolute_url')


class SubareaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sections = SectionSerializer(many=True)
    url = serializers.CharField(source='get_absolute_url')


class SubareaPreviewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    url = serializers.CharField(source='get_absolute_url')


class AreaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subareas = SubareaSerializer(many=True)
    url = serializers.CharField(source='get_absolute_url')


class AreaPreviewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    url = serializers.CharField(source='get_absolute_url')


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


class QuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='activity_id')
    title = serializers.CharField()
    url = serializers.CharField(source='get_absolute_url')


class ExercisePreviewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField(source='raw_text')
    url = serializers.CharField(source='get_absolute_url')
