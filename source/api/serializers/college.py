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
    # rooms = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    places = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    departments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    url = serializers.CharField(source='get_absolute_url')


class SimpleRoomSerializer(serializers.Serializer):
    # ^^^^^^ = Hides inheritance
    id = serializers.IntegerField()
    name = serializers.CharField()
    title = serializers.CharField(source='short_schedule_str')
    floor = serializers.IntegerField(allow_null=True)
    unlocked = serializers.BooleanField(allow_null=True)
    building = serializers.IntegerField(source='building_id')
    picture = serializers.ImageField()
    picture_cover = serializers.ImageField()
    door_number = serializers.IntegerField()
    url = serializers.CharField(source='get_absolute_url')


class RoomSerializer(serializers.Serializer):
    title = serializers.CharField(source='short_schedule_str')
    door_number = serializers.IntegerField()
    url = serializers.CharField(source='get_absolute_url')


class PlaceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    floor = serializers.IntegerField(allow_null=True)
    unlocked = serializers.BooleanField(allow_null=True)
    building = serializers.IntegerField(source='building_id')
    picture = serializers.ImageField()
    picture_cover = serializers.ImageField()
    room = RoomSerializer(allow_null=True)


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


class CurriculumSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    aggregation = serializers.JSONField(source='simple_aggregation')
    from_year = serializers.IntegerField()
    to_year = serializers.IntegerField()


class CourseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    description = serializers.CharField()
    department = serializers.IntegerField(source='department_id')
    degree = serializers.IntegerField()
    # degree_display = serializers.CharField(source='get_degree_display')
    external_url = serializers.CharField(source='url')
    url = serializers.CharField(source='get_absolute_url')
    current_curriculum = CurriculumSerializer(source='curriculum')


class ShiftInstanceSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    weekday = serializers.IntegerField()
    start = serializers.IntegerField()
    # start_str = serializers.CharField()
    duration = serializers.IntegerField()
    # end_str = serializers.CharField()
    room = serializers.IntegerField(source='room_id')


class ShiftSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    number = serializers.IntegerField()
    type = serializers.IntegerField(source='shift_type')
    # type_display = serializers.CharField(source='get_shift_type_display')
    teachers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    instances = ShiftInstanceSerializer(many=True)
    url = serializers.CharField(source='get_absolute_url')


class EnrollmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    class_instance = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    attendance = serializers.BooleanField()
    attendance_date = serializers.DateField()
    normal_grade = serializers.IntegerField()
    normal_grade_date = serializers.DateField()
    recourse_grade = serializers.IntegerField()
    recourse_grade_date = serializers.DateField()
    special_grade = serializers.IntegerField()
    special_grade_date = serializers.DateField()
    improvement_grade = serializers.IntegerField()
    improvement_grade_date = serializers.DateField()
    approved = serializers.BooleanField()
    grade = serializers.IntegerField()


class ClassInstanceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    parent = serializers.IntegerField(source='parent_id')
    period = serializers.IntegerField()
    year = serializers.IntegerField()
    information = serializers.JSONField()
    department = serializers.IntegerField(source='department_id')
    shifts = ShiftSerializer(many=True)
    enrollments = EnrollmentSerializer(many=True)
    avg_grade = serializers.IntegerField()
    url = serializers.CharField(source='get_absolute_url')


class ClassSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    credits = serializers.IntegerField()
    department = serializers.PrimaryKeyRelatedField(queryset=college.Department.objects, source='department_id')
    instances = serializers.PrimaryKeyRelatedField(queryset=college.ClassInstance.objects, many=True)
    url = serializers.CharField(source='get_absolute_url')
    external_id = serializers.IntegerField()


class DepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    building = serializers.PrimaryKeyRelatedField(read_only=True)
    classes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    courses = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    url = serializers.CharField(source='get_absolute_url')
    external_id = serializers.IntegerField()


class StudentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    number = serializers.IntegerField()
    enrollments = EnrollmentSerializer(many=True)
    shifts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    first_year = serializers.IntegerField()
    last_year = serializers.IntegerField()
    # course = serializers.IntegerField()
    course = serializers.PrimaryKeyRelatedField(read_only=True)
    credits = serializers.IntegerField()
    avg_grade = serializers.IntegerField()
    url = serializers.CharField(source='get_absolute_url')


class TeacherSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    short_name = serializers.CharField()
    abbreviation = serializers.CharField()
    first_year = serializers.IntegerField()
    last_year = serializers.IntegerField()
    phone = serializers.IntegerField()
    email = serializers.IntegerField()
    room = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    thumb = serializers.URLField(source='thumbnail_or_default')
    rank = serializers.CharField(source='rank.name', allow_null=True)
    departments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    shifts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    url = serializers.CharField(source='get_absolute_url')


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


class FileSerializer(serializers.Serializer):
    hash = serializers.CharField()
    size = serializers.IntegerField()
    mime = serializers.CharField()
    license = serializers.CharField(source='get_license_display')
    url = serializers.URLField(source='get_absolute_url')


class ClassFileSerializer(serializers.Serializer):
    id = serializers.CharField()
    file = FileSerializer()
    name = serializers.CharField()
    official = serializers.BooleanField()
    category = serializers.IntegerField()
    upload_datetime = serializers.DateTimeField()
    uploader = ProfileMinimalSerializer()
    uploader_teacher = TeacherSerializer()
    url = serializers.URLField(source='get_absolute_url')
