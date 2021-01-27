from rest_framework import serializers

import college.models as college
from api.serializers.users import ProfileMinimalSerializer
from college.models import Class


class DegreeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class BuildingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField(required=False)
    url = serializers.CharField(source='get_absolute_url')


class BuildingUsageSerializer(serializers.Serializer):
    usage = serializers.CharField()
    url = serializers.CharField()
    relevant = serializers.BooleanField()


class NestedRoomSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(source='short_schedule_str')
    type = serializers.IntegerField()
    floor = serializers.IntegerField()
    door_number = serializers.IntegerField()
    url = serializers.CharField(source='get_absolute_url')


class RoomSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    building = serializers.IntegerField(source='building_id')
    url = serializers.CharField(source='get_absolute_url')


class ClassMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ('id', 'name')


class CourseMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    # degree = DegreeSerializer()


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
    external_url = serializers.CharField(source='url')
    url = serializers.CharField(source='get_absolute_url')


class DepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    building = BuildingSerializer()
    classes = ClassMinimalSerializer(many=True)
    courses = CourseMinimalSerializer(many=True)
    url = serializers.CharField(source='get_absolute_url')


class ClassSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    credits = serializers.IntegerField()
    department = DepartmentMinimalSerializer()
    url = serializers.CharField(source='get_absolute_url')


class StudentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    number = serializers.IntegerField()
    course = CourseMinimalSerializer()
    url = serializers.CharField(source='get_absolute_url')


class TeacherSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    short_name = serializers.CharField()
    abbreviation = serializers.CharField()
    url = serializers.CharField(source='get_absolute_url')
    thumb = serializers.URLField(source='thumbnail_or_default')


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


class SimpleFileSerializer(serializers.Serializer):
    hash = serializers.CharField()
    size = serializers.IntegerField()
    mime = serializers.CharField()
    license = serializers.CharField(source='get_license_display')
    url = serializers.URLField(source='get_absolute_url')


class ClassFileSerializer(serializers.Serializer):
    id = serializers.CharField()
    file = SimpleFileSerializer()
    name = serializers.CharField()
    official = serializers.BooleanField()
    category = serializers.IntegerField()
    upload_datetime = serializers.DateTimeField()
    uploader = ProfileMinimalSerializer()
    uploader_teacher = TeacherSerializer()
    url = serializers.URLField(source='get_absolute_url')
