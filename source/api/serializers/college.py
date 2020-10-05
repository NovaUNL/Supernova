from rest_framework import serializers

import college.models as college
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


# class RoomMinimalSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField()
#     building = serializers.CharField()
#     degree = DegreeSerializer()


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


class ScheduleSerializer(serializers.ModelSerializer):
    # class_ = serializers.SlugRelatedField(
    #     read_only=True,
    #     slug_field='shift__class_instance__parent__name')
    # shift = serializers.SlugRelatedField(
    #     read_only=True,
    #     slug_field='shift__class_instance__parent__name')
    # id = serializers.IntegerField()
    # start = serializers.IntegerField()

    class_name = serializers.CharField(read_only=True, source="shift.class_instance.parent.name")
    shift_type = serializers.CharField(read_only=True, source="shift.get_shift_type_display")
    shift_number = serializers.IntegerField(read_only=True, source="shift.number")
    end = serializers.IntegerField()

    # weekday = serializers.IntegerField()
    # room = serializers.IntegerField()

    class Meta:
        model = college.ShiftInstance
        fields = ('id', 'start', 'end', 'weekday', 'class_name', 'shift_type', 'shift_number')
