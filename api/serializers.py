from rest_framework import serializers

from kleep.models import Class, Course


class BuildingMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField(required=False)


class ServiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=True)
    opening = serializers.IntegerField(required=False)
    lunch_start = serializers.IntegerField(required=False)
    lunch_end = serializers.IntegerField(required=False)
    closing = serializers.IntegerField(required=False)


class ServiceWithBuildingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=True)
    opening = serializers.IntegerField(required=False)
    lunch_start = serializers.IntegerField(required=False)
    lunch_end = serializers.IntegerField(required=False)
    closing = serializers.IntegerField(required=False)
    building = BuildingMinimalSerializer()


class BuildingWithServicesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField(required=False)
    service_set = ServiceSerializer(many=True)


class ClassMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ('id', 'name')


class CourseMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'name', 'abbreviation')


class DepartmentMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class CourseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    description = serializers.CharField()
    department = DepartmentMinimalSerializer()


class DepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    building = BuildingMinimalSerializer()
    class_set = ClassMinimalSerializer(many=True)
    course_set = CourseMinimalSerializer(many=True)


class ClassSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    credits = serializers.IntegerField()
    department = DepartmentMinimalSerializer()


class SynopsisTopicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class SynopsisSubareaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    synopsistopic_set = SynopsisTopicSerializer(many=True)


class SynopsisAreaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    synopsissubarea_set = SynopsisSubareaSerializer(many=True)


class SynopsisSectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class SynopsisTopicSectionsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    synopsissection_set = SynopsisSectionSerializer(many=True)
