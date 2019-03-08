from rest_framework import serializers

from college.models import Class


class DegreeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class BuildingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField(required=False)


class BuildingUsageSerializer(serializers.Serializer):
    usage = serializers.CharField()
    url = serializers.CharField()
    relevant = serializers.BooleanField()


class ClassMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ('id', 'name')


class CourseMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    degree = DegreeSerializer()


class DepartmentMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class CourseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    description = serializers.CharField()
    department = DepartmentMinimalSerializer()
    degree = DegreeSerializer()
    url = serializers.CharField()


class DepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    building = BuildingSerializer()
    class_set = ClassMinimalSerializer(many=True)
    course_set = CourseMinimalSerializer(many=True)


class ClassSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    credits = serializers.IntegerField()
    department = DepartmentMinimalSerializer()


class StudentSerializer(serializers.Serializer):
    abbreviation = serializers.CharField()
    number = serializers.IntegerField()
    course = CourseMinimalSerializer()
