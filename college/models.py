from datetime import datetime

from django.db import models
from django.db.models import Model, IntegerField, TextField, ForeignKey, ManyToManyField, BooleanField, OneToOneField, \
    CharField, FloatField, NullBooleanField

from clip import models as clip
from kleep.settings import COLLEGE_YEAR, COLLEGE_PERIOD
from users.models import User


class Student(Model):
    user = ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='students')
    number = IntegerField(null=True, blank=True)
    abbreviation = TextField(null=True, blank=True)
    course = ForeignKey('Course', on_delete=models.PROTECT, related_name='students')
    turns = ManyToManyField('Turn', through='TurnStudents')
    class_instances = ManyToManyField('ClassInstance', through='Enrollment')
    first_year = IntegerField(null=True, blank=True)
    last_year = IntegerField(null=True, blank=True)
    confirmed = BooleanField(default=False)
    clip_student = OneToOneField(clip.Student, on_delete=models.PROTECT, related_name='student')

    class Meta:
        ordering = ['number']
        unique_together = ('user', 'clip_student')

    def __str__(self):
        if self.user:
            return f'{self.number} - {self.abbreviation} ({self.user})'
        return f'{self.number} - {self.abbreviation}'


class Area(Model):
    name = TextField(max_length=200, unique=True)
    description = TextField(max_length=4096, null=True, blank=True)
    courses = ManyToManyField('Course', through='CourseArea')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Building(Model):
    name = TextField(max_length=30, unique=True)
    abbreviation = CharField(max_length=10, unique=True, null=True)
    map_tag = CharField(max_length=20, unique=True)
    clip_building = OneToOneField(clip.Building, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Place(Model):
    name = TextField(max_length=100)
    building = ForeignKey(Building, null=True, blank=True, on_delete=models.PROTECT, related_name='places')
    floor = IntegerField(default=0)
    unlocked = NullBooleanField(null=True, default=None)

    class Meta:
        unique_together = ('name', 'building')

    def __str__(self):
        return self.name

    def short_str(self):
        return f"{self.name} ({self.building.abbreviation})"


class Room(Place):
    capacity = IntegerField(null=True, blank=True)
    door_number = IntegerField(null=True, blank=True)
    clip_classroom = OneToOneField(clip.Classroom, null=True, blank=True, on_delete=models.PROTECT, related_name='room')

    UNKNOWN = 0
    CLASSROOM = 1
    AUDITORIUM = 2
    LABORATORY = 3

    TOPOLOGY_CHOICES = (
        (UNKNOWN, ''),
        (CLASSROOM, 'Sala'),
        (AUDITORIUM, 'Auditório'),
        (LABORATORY, 'Laboratório')
    )

    topology = IntegerField(choices=TOPOLOGY_CHOICES, default=0)
    description = TextField(max_length=2048, null=True, blank=True)
    equipment = TextField(max_length=2048, null=True, blank=True)

    class Meta:
        ordering = ('floor', 'door_number', 'name')

    def __str__(self):
        return f'{self.TOPOLOGY_CHOICES[self.topology][1]} {super().__str__()}'


class BuildingUsage(Model):  # TODO deprecate this model
    usage = TextField(max_length=100)
    building = ForeignKey(Building, on_delete=models.CASCADE)
    url = TextField(max_length=100, null=True, blank=True)
    relevant = BooleanField(default=False)

    class Meta:
        ordering = ('relevant',)

    def __str__(self):
        return "{} ({})".format(self.usage, self.building)


class Department(Model):
    name = TextField(max_length=100)
    description = TextField(max_length=4096, null=True, blank=True)
    building = ForeignKey(Building, on_delete=models.PROTECT, null=True, blank=True, related_name='departments')
    clip_department = OneToOneField(clip.Department, on_delete=models.PROTECT)
    img_url = TextField(null=True, blank=True)
    extinguished = BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(Model):
    name = TextField(max_length=200)
    description = TextField(max_length=4096, null=True, blank=True)
    degree = ForeignKey(clip.Degree, on_delete=models.PROTECT)
    abbreviation = TextField(max_length=100, null=True, blank=True)
    active = BooleanField(default=True)
    clip_course = OneToOneField(clip.Course, on_delete=models.PROTECT)
    department = ForeignKey('Department', on_delete=models.PROTECT, related_name='courses')
    areas = ManyToManyField(Area, through='CourseArea')
    url = TextField(max_length=256, null=True, blank=True)
    curriculum_classes = ManyToManyField('Class', through='Curriculum')
    extinguished = BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.degree.name} em {self.name}'


class CourseArea(Model):
    area = ForeignKey(Area, on_delete=models.PROTECT)
    course = ForeignKey(Course, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.course} -> {self.area}'


class Class(Model):
    name = TextField(max_length=30)
    abbreviation = TextField(max_length=10, default='---')
    description = TextField(max_length=1024, null=True, blank=True)
    credits = IntegerField(null=True, blank=True)  # 2 credits = 1 ECTS
    department = ForeignKey(Department, on_delete=models.PROTECT, null=True, related_name='classes')
    clip_class = OneToOneField(clip.Class, on_delete=models.PROTECT, related_name='related_class')
    courses = ManyToManyField(Course, through='Curriculum')
    extinguished = BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'classes'

    def __str__(self):
        return self.name


class Curriculum(Model):
    course = ForeignKey(Course, on_delete=models.CASCADE)
    corresponding_class = ForeignKey(Class, on_delete=models.PROTECT)  # Guess I can't simply call it 'class'
    period_type = CharField(max_length=1, null=True, blank=True)  # 's' => semester, 't' => trimester, 'a' => anual
    period = IntegerField(null=True, blank=True)
    year = IntegerField()
    required = BooleanField()

    class Meta:
        ordering = ['year', 'period_type', 'period']
        unique_together = ['course', 'corresponding_class']


class ClassInstance(Model):
    parent = ForeignKey(Class, on_delete=models.PROTECT, related_name='instances')
    period = ForeignKey(clip.Period, on_delete=models.PROTECT)
    year = IntegerField()
    clip_class_instance = OneToOneField(clip.ClassInstance, on_delete=models.PROTECT, related_name='class_instance')
    students = ManyToManyField(Student, through='Enrollment')

    class Meta:
        unique_together = ['parent', 'period', 'year']

    def __str__(self):
        return f"{self.parent.abbreviation}, {self.period} de {self.year}"

    def occasion(self):
        return f'{self.period}, {self.year-1}/{self.year}'


class Enrollment(Model):
    student = ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    class_instance = ForeignKey(ClassInstance, on_delete=models.CASCADE, related_name='enrollments')
    # u => unknown, r => reproved, n => approved@normal, e => approved@exam, s => approved@special
    result = CharField(default='u', max_length=1)
    grade = FloatField(null=True, blank=True)
    clip_enrollment = OneToOneField(clip.Enrollment, on_delete=models.PROTECT)

    class Meta:
        unique_together = ['student', 'class_instance']


class Turn(Model):
    class_instance = ForeignKey(ClassInstance, on_delete=models.CASCADE, related_name='turns')  # Eg: Analysis
    turn_type = ForeignKey(clip.TurnType, on_delete=models.PROTECT)  # Theoretical
    number = IntegerField()  # 1
    clip_turn = OneToOneField(clip.Turn, on_delete=models.PROTECT, related_name='turn')
    required = BooleanField(default=True)  # Optional attendance
    students = ManyToManyField(Student, through='TurnStudents')

    class Meta:
        unique_together = ['class_instance', 'turn_type', 'number']

    def __str__(self):
        return f"{self.class_instance} {self.turn_type.abbreviation.upper()}{self.number}"


class TurnStudents(Model):
    turn = ForeignKey(Turn, on_delete=models.CASCADE)
    student = ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'turn students'

    def __str__(self):
        return f'{self.student} enrolled to turn {self.turn}'


WEEKDAY_CHOICES = (
    (0, 'Segunda-feira'),
    (1, 'Terça-feira'),
    (2, 'Quarta-feira'),
    (3, 'Quinta-feira'),
    (4, 'Sexta-feira'),
    (5, 'Sábado-feira'),
    (6, 'Domingo-feira')
)


class TurnInstance(Model):
    turn = ForeignKey(Turn, on_delete=models.PROTECT, related_name='instances')  # Eg: Theoretical 1
    # TODO change to CASCADE *AFTER* the crawler is changed to update turn instances without deleting the previous ones
    clip_turn_instance = OneToOneField(clip.TurnInstance, on_delete=models.PROTECT, related_name='turn_instance')
    recurring = BooleanField(default=True)  # Always happens at the given day, hour and lasts for k minutes
    # Whether this is a recurring turn
    weekday = IntegerField(null=True, blank=True, choices=WEEKDAY_CHOICES)  # 0 - Monday
    start = IntegerField(null=True, blank=True)  # 8*60+30 = 8:30 AM
    duration = IntegerField(null=True, blank=True)  # 60 minutes
    # --------------
    room = ForeignKey(Room, on_delete=models.PROTECT, null=True, blank=True, related_name='turn_instances')

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
        return WEEKDAY_CHOICES[self.weekday][1]

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
