from datetime import datetime

from django.db import models as djm
from django.contrib.gis.db import models as gis
from django.contrib.postgres import fields as pgm
from django.core.serializers.json import DjangoJSONEncoder
from clip import models as clip
from settings import COLLEGE_YEAR, COLLEGE_PERIOD
from users.models import User
from . import choice_types as ctypes


class Student(djm.Model):
    user = djm.ForeignKey(User, null=True, on_delete=djm.CASCADE, related_name='students')
    number = djm.IntegerField(null=True, blank=True)
    abbreviation = djm.CharField(null=True, blank=True, max_length=64)
    course = djm.ForeignKey('Course', on_delete=djm.PROTECT, related_name='students', null=True, blank=True)
    turns = djm.ManyToManyField('Turn', through='TurnStudents')
    class_instances = djm.ManyToManyField('ClassInstance', through='Enrollment')
    first_year = djm.IntegerField(null=True, blank=True)
    last_year = djm.IntegerField(null=True, blank=True)
    confirmed = djm.BooleanField(default=False)
    graduation_grade = djm.IntegerField(null=True, blank=True, default=None)
    clip_student = djm.OneToOneField(clip.Student, on_delete=djm.PROTECT, related_name='student')

    class Meta:
        ordering = ['number']
        unique_together = ('user', 'clip_student')

    def __str__(self):
        if self.user:
            return f'{self.number} - {self.abbreviation} ({self.user})'
        return f'{self.number} - {self.abbreviation}'


class Area(djm.Model):
    name = djm.CharField(max_length=200, unique=True)
    description = djm.TextField(max_length=4096, null=True, blank=True)
    courses = djm.ManyToManyField('Course', through='CourseArea')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


def building_pic_path(building, filename):
    return f'c/b/{building.id}/pic.{filename.split(".")[-1]}'


class Building(djm.Model):
    name = djm.CharField(max_length=32, unique=True)
    abbreviation = djm.CharField(max_length=16, unique=True, null=True)
    map_tag = djm.CharField(max_length=20, unique=True)
    location = gis.PointField(geography=True, null=True)
    clip_building = djm.OneToOneField(clip.Building, null=True, blank=True, on_delete=djm.PROTECT)
    map = djm.URLField(null=True, blank=True, default=None)
    picture = djm.ImageField(upload_to=building_pic_path, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


def department_pic_path(department, filename):
    return f'c/d/{department.id}/pic.{filename.split(".")[-1]}'


class Department(djm.Model):
    name = djm.CharField(max_length=128)
    description = djm.TextField(max_length=4096, null=True, blank=True)
    building = djm.ForeignKey(Building, on_delete=djm.PROTECT, null=True, blank=True, related_name='departments')
    clip_department = djm.OneToOneField(clip.Department, on_delete=djm.PROTECT)
    extinguished = djm.BooleanField(default=True)
    picture = djm.ImageField(upload_to=department_pic_path, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Place(djm.Model):
    name = djm.CharField(max_length=128)
    building = djm.ForeignKey(Building, null=True, blank=True, on_delete=djm.PROTECT, related_name='places')
    floor = djm.IntegerField(default=0)
    unlocked = djm.NullBooleanField(null=True, default=None)
    location = gis.PointField(geography=True, null=True, blank=True)

    def __str__(self):
        return f'{self.name} ({self.building})'

    def short_str(self):
        return f"{self.name} ({self.building.abbreviation})"


def room_pic_path(room, filename):
    return f'c/b/{room.id}/pic.{filename.split(".")[-1]}'


class Room(Place):
    department = djm.ForeignKey(Department, on_delete=djm.PROTECT, related_name='rooms', null=True, blank=True)
    capacity = djm.IntegerField(null=True, blank=True)
    door_number = djm.IntegerField(null=True, blank=True)
    clip_room = djm.OneToOneField(clip.Room, null=True, blank=True, on_delete=djm.PROTECT, related_name='room')

    type = djm.IntegerField(choices=ctypes.RoomType.CHOICES, default=0)
    description = djm.TextField(max_length=2048, null=True, blank=True)
    equipment = djm.TextField(max_length=2048, null=True, blank=True)
    features = djm.ManyToManyField('Feature', blank=True)
    extinguished = djm.BooleanField(default=False)
    picture = djm.ImageField(upload_to=room_pic_path, null=True, blank=True)

    class Meta:
        ordering = ('floor', 'door_number', 'name')
        # unique_together = ('name', 'building', 'type') inheritance forbids this

    def __str__(self):
        return f'{ctypes.RoomType.CHOICES[self.type-1][1]} {self.name}'

    def long__str(self):
        return f'{ctypes.RoomType.CHOICES[self.type-1][1]} {super().__str__()}'


class Course(djm.Model):
    name = djm.CharField(max_length=256)
    description = djm.TextField(max_length=4096, null=True, blank=True)
    degree = djm.IntegerField(choices=ctypes.Degree.CHOICES)
    abbreviation = djm.CharField(max_length=128, null=True, blank=True)
    active = djm.BooleanField(default=False)
    clip_course = djm.OneToOneField(clip.Course, on_delete=djm.PROTECT)
    department = djm.ForeignKey('Department', null=True, blank=True, on_delete=djm.PROTECT, related_name='courses')
    areas = djm.ManyToManyField(Area, through='CourseArea')
    url = djm.URLField(max_length=256, null=True, blank=True)
    curriculum_classes = djm.ManyToManyField('Class', through='Curriculum')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{ctypes.Degree.name(self.degree)} em {self.name}'


class CourseArea(djm.Model):
    area = djm.ForeignKey(Area, on_delete=djm.PROTECT)
    course = djm.ForeignKey(Course, on_delete=djm.PROTECT)

    def __str__(self):
        return f'{self.course} -> {self.area}'


class Class(djm.Model):
    name = djm.CharField(max_length=64)
    abbreviation = djm.CharField(max_length=16, default='---')
    description = djm.TextField(max_length=1024, null=True, blank=True)
    credits = djm.IntegerField(null=True, blank=True)  # 2 credits = 1 ECTS
    department = djm.ForeignKey(Department, on_delete=djm.PROTECT, null=True, related_name='classes')
    clip_class = djm.OneToOneField(clip.Class, on_delete=djm.PROTECT, related_name='related_class')
    courses = djm.ManyToManyField(Course, through='Curriculum')
    extinguished = djm.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'classes'

    def __str__(self):
        return self.name


class Curriculum(djm.Model):
    course = djm.ForeignKey(Course, on_delete=djm.CASCADE)
    corresponding_class = djm.ForeignKey(Class, on_delete=djm.PROTECT)  # Guess I can't simply call it 'class'
    period_type = djm.CharField(max_length=1, null=True, blank=True)  # 's' => semester, 't' => trimester, 'a' => anual
    period = djm.IntegerField(null=True, blank=True)
    year = djm.IntegerField()
    required = djm.BooleanField()

    class Meta:
        ordering = ['year', 'period_type', 'period']
        unique_together = ['course', 'corresponding_class']


class ClassInstance(djm.Model):
    parent = djm.ForeignKey(Class, on_delete=djm.PROTECT, related_name='instances')
    period = djm.IntegerField(choices=ctypes.Period.CHOICES)
    year = djm.IntegerField()
    clip_class_instance = djm.OneToOneField(clip.ClassInstance, on_delete=djm.PROTECT, related_name='class_instance')
    students = djm.ManyToManyField(Student, through='Enrollment')
    information = pgm.JSONField(encoder=DjangoJSONEncoder)

    class Meta:
        unique_together = ['parent', 'period', 'year']

    def __str__(self):
        return f"{self.parent.abbreviation}, {self.period} de {self.year}"

    def occasion(self):
        return f'{ctypes.Period.CHOICES[self.period-1][1]}, {self.year-1}/{self.year}'


class Enrollment(djm.Model):
    student = djm.ForeignKey(Student, on_delete=djm.CASCADE, related_name='enrollments')
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.CASCADE, related_name='enrollments')
    # u => unknown, r => reproved, n => approved@normal, e => approved@exam, s => approved@special
    result = djm.CharField(default='u', max_length=1)
    grade = djm.FloatField(null=True, blank=True)
    clip_enrollment = djm.OneToOneField(clip.Enrollment, on_delete=djm.PROTECT)

    class Meta:
        unique_together = ['student', 'class_instance']


class Turn(djm.Model):
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.CASCADE, related_name='turns')  # Eg: Analysis
    turn_type = djm.IntegerField(choices=ctypes.TurnType.CHOICES)  # Theoretical
    number = djm.IntegerField()  # 1
    clip_turn = djm.OneToOneField(clip.Turn, on_delete=djm.CASCADE, related_name='turn')
    required = djm.BooleanField(default=True)  # Optional attendance
    students = djm.ManyToManyField(Student, through='TurnStudents')

    class Meta:
        unique_together = ['class_instance', 'turn_type', 'number']

    def __str__(self):
        return f"{self.class_instance} {ctypes.TurnType.abbreviation(self.turn_type)}{self.number}"

    def type_abbreviation(self):
        return ctypes.TurnType.abbreviation(self.turn_type)


class TurnStudents(djm.Model):
    turn = djm.ForeignKey(Turn, on_delete=djm.CASCADE)
    student = djm.ForeignKey(Student, on_delete=djm.CASCADE)

    class Meta:
        verbose_name_plural = 'turn students'

    def __str__(self):
        return f'{self.student} enrolled to turn {self.turn}'


class TurnInstance(djm.Model):
    turn = djm.ForeignKey(Turn, on_delete=djm.CASCADE, related_name='instances')  # Eg: Theoretical 1
    # TODO change to CASCADE *AFTER* the crawler is changed to update turn instances without deleting the previous ones
    clip_turn_instance = djm.OneToOneField(clip.TurnInstance, on_delete=djm.CASCADE, related_name='turn_instance')
    recurring = djm.BooleanField(default=True)  # Always happens at the given day, hour and lasts for k minutes
    # Whether this is a recurring turn
    weekday = djm.IntegerField(null=True, blank=True, choices=ctypes.WEEKDAY_CHOICES)  # 0 - Monday
    start = djm.IntegerField(null=True, blank=True)  # 8*60+30 = 8:30 AM
    duration = djm.IntegerField(null=True, blank=True)  # 60 minutes
    # --------------
    room = djm.ForeignKey(Room, on_delete=djm.PROTECT, null=True, blank=True, related_name='turn_instances')

    class Meta:
        ordering = ['weekday', 'start']

    def __str__(self):
        return f"{self.turn}, d{self.weekday}, {self.minutes_to_str(self.start)}"

    def intersects(self, turn_instance):
        # Same weekday AND A starts before B ends and B starts before A ends
        return self.weekday == turn_instance.weekday and \
               self.start < turn_instance.start + turn_instance.duration and \
               turn_instance.start < self.start + self.duration

    def weekday_pt(self):
        return ctypes.WEEKDAY_CHOICES[self.weekday][1]

    def start_str(self):
        return self.minutes_to_str(self.start)

    def end_str(self):
        return self.minutes_to_str(self.start + self.duration)

    def happening(self):
        now = datetime.now()
        if not (self.turn.class_instance.year == COLLEGE_YEAR and self.turn.class_instance.period == COLLEGE_PERIOD):
            return False

        # same weekday and within current time interval
        return self.weekday == now.isoweekday() and self.start < now.hour * 60 + now.min < self.start + self.duration

    @staticmethod
    def minutes_to_str(minutes):
        return "%02d:%02d" % (minutes // 60, minutes % 60)


class Teacher(djm.Model):
    """
    | A person who teaches.
    | Note that there is an intersection between students and teachers. A student might become a teacher.
    """
    iid = djm.IntegerField()
    name = djm.TextField(max_length=100)
    # This isn't really a M2M, but the crawler tables are unmodifiable
    clip_teachers = djm.ManyToManyField(clip.Teacher)
    #: Departments this teacher has worked for
    departments = djm.ManyToManyField(Department)

    def __str__(self):
        return f"{self.name} ({self.iid})"


class File(djm.Model):
    name = djm.CharField(null=True, max_length=256)
    type = djm.IntegerField(db_column='file_type', choices=ctypes.FileType.CHOICES)
    size = djm.IntegerField()
    hash = djm.CharField(max_length=40, null=True)
    location = djm.TextField(null=True)
    mime = djm.TextField(null=True)
    clip_file = djm.ForeignKey(clip.File, on_delete=djm.CASCADE)
    class_instances = djm.ManyToManyField(ClassInstance, through='ClassInstanceFile')


class ClassInstanceFile(djm.Model):
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.PROTECT)
    file = djm.ForeignKey(File, on_delete=djm.PROTECT, db_column='file_id')
    upload_datetime = djm.DateTimeField()
    uploader = djm.CharField(max_length=100)


class ClassEvaluation(djm.Model):
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.PROTECT)
    datetime = djm.DateTimeField()
    type = djm.IntegerField(db_column='evaluation_type', choices=ctypes.EvaluationType.CHOICES)


class ClassInstanceMessages(djm.Model):
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.PROTECT)
    teacher = djm.ForeignKey(Teacher, on_delete=djm.PROTECT, db_column='teacher_id')
    title = djm.CharField(max_length=256)
    message = djm.TextField()
    upload_datetime = djm.DateTimeField()
    uploader = djm.CharField(max_length=128)
    datetime = djm.DateTimeField()
    clip_message = djm.ForeignKey(clip.ClassInstanceMessages, on_delete=djm.CASCADE)


def feature_pic_path(feature, filename):
    return f'c/f/{feature.id}.{filename.split(".")[-1]}'


class Feature(djm.Model):
    name = djm.CharField(max_length=100)
    description = djm.TextField()
    icon = djm.FileField(upload_to=feature_pic_path)

    def __str__(self):
        return self.name
