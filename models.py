from datetime import date

from ckeditor.fields import RichTextField
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User as SysUser
from django.db.models import Model, IntegerField, TextField, ForeignKey, DateTimeField, ManyToManyField, DateField, \
    BooleanField, OneToOneField, TimeField, CharField, FloatField, NullBooleanField

CLIPY_TABLE_PREFIX = 'clip_'
KLEEP_TABLE_PREFIX = 'kleep_'


# CLIPy Models (Unmanaged)
# TODO CLIPy unique constraints
class TemporalEntity:
    first_year = IntegerField(blank=True, null=True)
    last_year = IntegerField(blank=True, null=True)

    def has_time_range(self):
        return not (self.first_year is None or self.last_year is None)


class Degree(Model):
    id = IntegerField(primary_key=True)
    internal_id = TextField(null=True, max_length=5)
    name = TextField()

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'degrees'

    def __str__(self):
        return self.name


class Period(Model):
    id = IntegerField(primary_key=True)
    part = IntegerField()
    parts = IntegerField()
    letter = TextField()
    start_month = IntegerField(null=True)
    end_month = IntegerField(null=True)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'periods'

    def __str__(self):
        if self.id == 1:
            return f' Ano'
        elif self.id <= 3:
            return f'{self.part}º Semestre'
        else:
            return f'{self.part}º Trimestre'


class TurnType(Model):
    id = IntegerField(primary_key=True)
    name = TextField(max_length=30)
    abbreviation = TextField(max_length=5)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_types'

    def __str__(self):
        return self.abbreviation


class ClipInstitution(TemporalEntity, Model):
    id = IntegerField(primary_key=True)
    internal_id = IntegerField()
    abbreviation = TextField(max_length=10)
    name = TextField(null=True, max_length=50)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'institutions'

    def __str__(self):
        return self.abbreviation


class ClipBuilding(Model):
    id = IntegerField(primary_key=True)
    name = TextField(max_length=30)
    institution = ForeignKey('ClipInstitution', on_delete=models.PROTECT, db_column='institution_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'buildings'

    def __str__(self):
        return self.name


class ClipDepartment(Model, TemporalEntity):
    id = IntegerField(primary_key=True)
    internal_id = TextField()
    name = TextField(max_length=50)
    institution = ForeignKey(ClipInstitution, on_delete=models.PROTECT, db_column='institution_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'departments'

    def __str__(self):
        return "{}({})".format(self.name, self.internal_id)


class ClipClass(Model):
    id = IntegerField(primary_key=True)
    name = TextField(null=True)
    internal_id = TextField(null=True)
    department = ForeignKey(ClipDepartment, on_delete=models.PROTECT, db_column='department_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'classes'

    def __str__(self):
        return "{}({})".format(self.name, self.internal_id)


class ClipClassroom(Model):
    id = IntegerField(primary_key=True)
    name = TextField(max_length=70)
    building = ForeignKey('ClipBuilding', on_delete=models.PROTECT, db_column='building_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'classrooms'

    def __str__(self):
        return "{} - {}".format(self.name, self.building.name)


class ClipTeacher(Model):
    __tablename__ = CLIPY_TABLE_PREFIX + 'teachers'
    id = IntegerField(primary_key=True)
    name = TextField(max_length=100)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'teachers'

    def __str__(self):
        return self.name


class ClipClassInstance(Model):
    id = IntegerField(primary_key=True)
    parent = ForeignKey(ClipClass, on_delete=models.PROTECT, db_column='class_id')
    period = ForeignKey(Period, on_delete=models.PROTECT, db_column='period_id')
    year = IntegerField()

    # regent = ForeignKey(ClipTeacher, on_delete=models.PROTECT, db_column='regent_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'class_instances'

    def __str__(self):
        return "{} ({} of {})".format(self.parent, self.period, self.year)


class ClipCourse(TemporalEntity, Model):
    id = IntegerField(primary_key=True)
    internal_id = IntegerField()
    name = TextField(max_length=70)
    abbreviation = TextField(null=True, max_length=15)
    institution = ForeignKey(ClipInstitution, on_delete=models.PROTECT, db_column='institution_id')
    degree = ForeignKey(Degree, on_delete=models.PROTECT, db_column='degree_id', null=True, blank=True)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'courses'

    def __str__(self):
        return "{}(ID:{} Abbreviation:{}, Degree:{})".format(self.name, self.internal_id, self.abbreviation,
                                                             self.degree)


class ClipStudent(Model):
    id = IntegerField(primary_key=True)
    name = TextField()
    internal_id = IntegerField()
    abbreviation = TextField(null=True, max_length=30)
    course = ForeignKey(ClipCourse, on_delete=models.PROTECT, db_column='course_id')
    institution = ForeignKey(ClipInstitution, on_delete=models.PROTECT, db_column='institution_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'students'

    def __str__(self):
        return "{}, {}".format(self.name, self.internal_id, self.abbreviation)


class ClipAdmission(Model):
    id = IntegerField(primary_key=True)
    student = ForeignKey(ClipStudent, on_delete=models.PROTECT, db_column='student_id')
    course = ForeignKey(ClipCourse, on_delete=models.PROTECT, db_column='course_id')
    phase = IntegerField(null=True)
    year = IntegerField(null=True)
    option = IntegerField(null=True)
    state = TextField(null=True, max_length=50)
    check_date = DateTimeField()
    name = TextField(null=True, max_length=100)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'admissions'

    def __str__(self):
        return ("{}, admitted to {}({}) (option {}) at the phase {} of the {} contest. {} as of {}".format(
            (self.student.name if self.student_id is not None else self.name),
            self.course.abbreviation, self.course_id, self.option, self.phase, self.year, self.state,
            self.check_date))


class ClipEnrollment(Model):
    id = IntegerField(primary_key=True)
    student = ForeignKey(ClipStudent, on_delete=models.PROTECT, db_column='student_id')
    class_instance = ForeignKey(ClipClassInstance, on_delete=models.PROTECT, db_column='class_instance_id')
    attempt = IntegerField(null=True)
    student_year = IntegerField(null=True)
    statutes = TextField(blank=True, null=True, max_length=20)
    observation = TextField(blank=True, null=True, max_length=30)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'enrollments'

    def __str__(self):
        return "{} enrolled to {}, attempt:{}, student year:{}, statutes:{}, obs:{}".format(
            self.student, self.class_instance, self.attempt, self.student_year, self.statutes, self.observation)


class ClipTurn(Model):
    id = IntegerField(primary_key=True)
    number = IntegerField()
    type = ForeignKey(TurnType, on_delete=models.PROTECT, db_column='type_id')
    class_instance = ForeignKey(ClipClassInstance, on_delete=models.PROTECT, db_column='class_instance_id')
    minutes = IntegerField(null=True)
    enrolled = IntegerField(null=True)
    capacity = IntegerField(null=True)
    routes = TextField(blank=True, null=True, max_length=30)
    restrictions = TextField(blank=True, null=True, max_length=30)
    state = TextField(blank=True, null=True, max_length=30)
    students = ManyToManyField(ClipStudent, through='ClipTurnStudent')
    teachers = ManyToManyField(ClipTeacher, through='ClipTurnTeacher')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turns'

    def __str__(self):
        return "{}{} of {}".format(self.type.abbreviation.upper(), self.number, self.class_instance)


class ClipTurnInstance(Model):
    id = IntegerField(primary_key=True)
    turn = ForeignKey(ClipTurn, on_delete=models.PROTECT, db_column='turn_id')
    start = IntegerField()
    end = IntegerField(null=True)
    weekday = IntegerField(null=True)
    classroom = ForeignKey(ClipClassroom, on_delete=models.PROTECT, db_column='classroom_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_instances'


class ClipTurnTeacher(Model):
    turn = ForeignKey(ClipTurn, on_delete=models.PROTECT)
    teacher = ForeignKey(ClipTeacher, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_students'


class ClipTurnStudent(Model):
    turn = ForeignKey(ClipTurn, on_delete=models.PROTECT, db_column='turn_id')
    student = ForeignKey(ClipStudent, on_delete=models.PROTECT, db_column='student_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_students'


# MANAGED MODELS

class User(Model):
    name = TextField()
    nickname = TextField()
    birth_date = DateField()
    sys_user = ForeignKey(SysUser, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "{} ({})".format(self.nickname, self.name)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'users'


class Student(Model):
    # A student can exist without having an account
    user = OneToOneField(User, on_delete=models.CASCADE)
    crawled_students = ManyToManyField(ClipStudent, through='StudentClipStudent')
    turns = ManyToManyField('Turn', through='TurnStudents')
    class_instances = ManyToManyField('ClassInstance', through='Enrollment')
    courses = ManyToManyField('Course', through='StudentCourse')
    single_clip_student = BooleanField(default=True)
    number = IntegerField(null=True, blank=True)  # These can be null if this student maps to various clip students
    abbreviation = TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'students'

    def __str__(self):
        return str(self.user)


class StudentClipStudent(Model):
    clip_student = ForeignKey(ClipStudent, on_delete=models.PROTECT)
    student = ForeignKey(Student, on_delete=models.CASCADE)
    confirmed = BooleanField(default=False)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'student_clip_students'


class Area(Model):
    name = TextField(max_length=200)
    description = TextField(max_length=4096, null=True, blank=True)
    variants = ManyToManyField('Course', through='CourseArea')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'areas'

    def __str__(self):
        return self.name


class Building(Model):
    name = TextField(max_length=30, unique=True)
    abbreviation = TextField(max_length=10, unique=True, null=True)
    map_tag = TextField(max_length=20)
    clip_building = OneToOneField(ClipBuilding, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'buildings'

    def __str__(self):
        return self.name


class Place(Model):
    name = TextField(max_length=100)
    building = ForeignKey(Building, on_delete=models.CASCADE)
    clip_classroom = OneToOneField(ClipClassroom, null=True, blank=True, on_delete=models.PROTECT)
    unlocked = NullBooleanField(null=True, default=None)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'places'
        ordering = ('building', 'name',)

    def __str__(self):
        return f"{self.building} {self.name}"

    def short_str(self):
        return f"{self.name}\n{self.building.abbreviation}"


class Classroom(Place):
    capacity = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'classrooms'


class Auditorium(Place):
    capacity = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'auditoriums'


class Laboratory(Place):
    description = TextField(max_length=2048)
    equipment = TextField(max_length=2048)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'laboratories'


class BuildingUsage(Model):
    usage = TextField(max_length=100)
    building = ForeignKey(Building, on_delete=models.CASCADE)
    url = TextField(max_length=100, null=True, blank=True)
    relevant = BooleanField(default=False)

    class Meta:
        managed = True
        ordering = ['relevant']
        db_table = KLEEP_TABLE_PREFIX + 'building_usages'

    def __str__(self):
        return "{} ({})".format(self.usage, self.building)


class Department(Model):
    name = TextField(max_length=100)
    description = TextField(max_length=1024, null=True, blank=True)
    building = ForeignKey(Building, on_delete=models.PROTECT, null=True, blank=True)
    clip_department = OneToOneField(ClipDepartment, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'departments'

    def __str__(self):
        return self.name


class Course(Model):
    name = TextField(max_length=200)
    description = TextField(max_length=4096, null=True, blank=True)
    degree = ForeignKey(Degree, on_delete=models.PROTECT)
    abbreviation = TextField(max_length=100, null=True, blank=True)
    active = BooleanField(default=True)
    clip_course = ForeignKey(ClipCourse, on_delete=models.PROTECT, related_name='crawled_course')
    department = ForeignKey('Department', on_delete=models.PROTECT)
    areas = ManyToManyField(Area, through='CourseArea')
    url = TextField(max_length=256, null=True, blank=True)
    students = ManyToManyField(Student, through='StudentCourse')
    curriculum = ManyToManyField('Class', through='Curriculum')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'courses'

    def __str__(self):
        return f'{self.degree.name} em {self.name}'


class StudentCourse(Model):
    student = ForeignKey(Student, on_delete=models.CASCADE)
    course = ForeignKey(Course, on_delete=models.PROTECT)
    first_year = IntegerField()
    last_year = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'student_courses'

    def __str__(self):
        return f'{self.student}@{self.course} {self.first_year}-{self.last_year}'


class CourseArea(Model):
    area = ForeignKey(Area, on_delete=models.PROTECT)
    course = ForeignKey(Course, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'course_areas'

    def __str__(self):
        return f'{self.course} -> {self.area}'


class Class(Model):
    name = TextField(max_length=30)
    abbreviation = TextField(max_length=10, default='HELP')
    description = TextField(max_length=1024, null=True, blank=True)
    credits = IntegerField(null=True, blank=True)
    department = ForeignKey(Department, on_delete=models.PROTECT, null=True)
    clip_class = OneToOneField(ClipClass, on_delete=models.PROTECT, related_name='related_class')
    courses = ManyToManyField(Course, through='Curriculum')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'classes'

    def __str__(self):
        return self.name


class Curriculum(Model):
    course = ForeignKey(Course, on_delete=models.CASCADE, related_name='course')
    corresponding_class = ForeignKey(Class, on_delete=models.PROTECT)  # Guess I can't simply call it 'class'
    period_type = CharField(max_length=1, null=True, blank=True)  # 's' => semester, 't' => trimester, 'a' => anual
    period = IntegerField(null=True, blank=True)
    year = IntegerField()
    required = BooleanField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'curriculum'


class ClassInstance(Model):
    parent = ForeignKey(Class, on_delete=models.PROTECT)
    period = ForeignKey(Period, on_delete=models.PROTECT)
    year = IntegerField()
    clip_class_instance = OneToOneField(ClipClassInstance, on_delete=models.PROTECT)
    students = ManyToManyField(Student, through='Enrollment')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'class_instances'

    def __str__(self):
        return f"{self.parent.abbreviation}, {self.period} de {self.year}"

    def occasion(self):
        return f'{self.period}, {self.year-1}/{self.year}'


class Enrollment(Model):
    student = ForeignKey(Student, on_delete=models.CASCADE)
    class_instance = ForeignKey(ClassInstance, on_delete=models.CASCADE)
    # u => unknown, r => reproved, n => approved@normal, e => approved@exam, s => approved@special
    result = CharField(default='u', max_length=1)
    grade = FloatField(null=True, blank=True)
    clip_enrollment = ForeignKey(ClipEnrollment, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'enrollments'


class Turn(Model):
    class_instance = ForeignKey(ClassInstance, on_delete=models.CASCADE)  # Eg: Analysis
    turn_type = ForeignKey(TurnType, on_delete=models.PROTECT)  # Theoretical
    number = IntegerField()  # 1
    clip_turn = OneToOneField(ClipTurn, on_delete=models.PROTECT)
    required = BooleanField(default=True)  # Optional attendance
    students = ManyToManyField(Student, through='TurnStudents')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'turns'

    def __str__(self):
        return f"{self.class_instance} {self.turn_type.abbreviation.upper()}{self.number}"


class TurnStudents(Model):
    turn = ForeignKey(Turn, on_delete=models.CASCADE)
    student = ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'turn_students'

    def __str__(self):
        return f'{self.student} enrolled to turn {self.turn}'


class TurnInstance(Model):
    turn = ForeignKey(Turn, on_delete=models.PROTECT)  # Eg: Theoretical 1
    # TODO change to CASCADE *AFTER* the crawler is changed to update turn instances without deleting the previous ones
    clip_turn_instance = OneToOneField(ClipTurnInstance, on_delete=models.PROTECT)
    recurring = BooleanField(default=True)  # Always happens at the given day, hour and lasts for k minutes
    # Whether this is a recurring turn
    weekday = IntegerField(null=True, blank=True)  # 1 - Monday
    start = IntegerField(null=True, blank=True)  # 8*60+30 = 8:30 AM
    duration = IntegerField(null=True, blank=True)  # 60 minutes
    # --------------
    classroom = ForeignKey(Place, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'turn_instances'

    def __str__(self):
        return f"{self.turn}, d{self.weekday}, {self.minutes_to_str(self.start)}"

    def intersects(self, turn_instance):
        # Same weekday AND A starts before B ends and B starts before A ends
        return self.weekday == turn_instance.weekday and \
               self.start < turn_instance.start + turn_instance.duration and \
               turn_instance.start < self.start + self.duration

    def weekday_pt(self):
        if self.weekday == 0:
            return 'Segunda-feira'
        elif self.weekday == 1:
            return 'Terça-feira'
        elif self.weekday == 2:
            return 'Quarta-feira'
        elif self.weekday == 3:
            return 'Quinta-feira'
        elif self.weekday == 4:
            return 'Sexta-feira'
        elif self.weekday == 5:
            return 'Sábado'
        elif self.weekday == 6:
            return 'Domingo'

    def start_str(self):
        return self.minutes_to_str(self.start)

    def end_str(self):
        return self.minutes_to_str(self.start + self.duration)

    @staticmethod
    def minutes_to_str(minutes):
        return "%02d:%02d" % (minutes // 60, minutes % 60)


class Event(Model):
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()
    announce_date = DateField(default=date.today)
    classroom = ForeignKey(Place, null=True, blank=True, on_delete=models.SET_NULL)
    users = ManyToManyField(User, through='EventUsers')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'events'

    def __str__(self):
        return f'from {self.datetime_to_eventtime(self.start_datetime)} ' \
               f'to {self.datetime_to_eventtime(self.end_datetime)}'

    def interval(self):
        if self.start_datetime.day == self.end_datetime.day:
            return '%02d-%02d %02d:%02d - %02d:%02d' % (self.start_datetime.day, self.start_datetime.month,
                                                        self.start_datetime.hour, self.start_datetime.minute,
                                                        self.end_datetime.hour, self.end_datetime.minute)

        return '%02d-%02d %02d:%02d - %02d-%02d %02d:%02d' % (self.start_datetime.day, self.start_datetime.month,
                                                              self.start_datetime.hour, self.start_datetime.minute,
                                                              self.end_datetime.day, self.end_datetime.month,
                                                              self.end_datetime.hour, self.end_datetime.minute)

    @staticmethod
    def datetime_to_eventtime(datetime):  # TODO move me somewhere else
        return '%02d-%02d, %02d:%02d' % (datetime.day, datetime.month, datetime.hour, datetime.minute)


class EventUsers(Model):
    event = ForeignKey(Event, on_delete=models.CASCADE)
    user = ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'event_users'


class TurnEvent(Event):
    turn_instance = ForeignKey(TurnInstance, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'turn_events'


class Workshop(Model):
    name = TextField(max_length=100)
    description = TextField(max_length=4096, null=True, blank=True)
    capacity = IntegerField(null=True, blank=True)
    creator = ForeignKey('Group', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'workshops'

    def __str__(self):
        return self.name


class WorkshopEvent(Event):
    workshop = ForeignKey(Workshop, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'workshop_events'


class Party(Model):
    name = TextField(max_length=100)
    description = TextField(max_length=4096, null=True, blank=True)
    capacity = IntegerField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'parties'

    def __str__(self):
        return self.name


class PartyEvent(Event):
    party = ForeignKey(Party, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'party_events'


class Service(Model):
    name = TextField(max_length=50)
    building = ForeignKey(Building, null=True, blank=True, on_delete=models.SET_NULL)
    map_tag = TextField(max_length=15)
    opening = TimeField(null=True, blank=True)
    lunch_start = TimeField(null=True, blank=True)  # For a bar this is the meal time, for other places this is a break
    lunch_end = TimeField(null=True, blank=True)
    closing = TimeField(null=True, blank=True)
    open_saturday = BooleanField(default=False)
    open_sunday = BooleanField(default=False)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'services'

    def __str__(self):
        return "{} ({})".format(self.name, self.building)


class Bar(Model):
    service = OneToOneField(Service, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'bars'

    def __str__(self):
        return str(self.service)


class BarDailyMenu(Model):
    bar = ForeignKey(Bar, on_delete=models.CASCADE)
    date = DateField(auto_now_add=True)
    item = TextField(max_length=100)
    price = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'bar_daily_menus'

    def __str__(self):
        return f'{self.item}, {self.bar} ({self.date})'


class BarPrice(Model):
    bar = ForeignKey(Bar, on_delete=models.CASCADE)
    item = TextField(max_length=100)
    price = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'bar_prices'

    def __str__(self):
        return '%s, %0.2f€ (%s)' % (self.item, self.price / 100, self.bar.service.name)


class SynopsisArea(Model):
    name = TextField(max_length=50)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_area'

    def __str__(self):
        return self.name


class SynopsisSubarea(Model):
    name = TextField(max_length=50)
    description = TextField(max_length=1024)
    area = ForeignKey(SynopsisArea, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_subarea'

    def __str__(self):
        return self.name


class SynopsisTopic(Model):
    name = TextField()
    index = IntegerField()
    sub_area = ForeignKey(SynopsisSubarea, on_delete=models.PROTECT)
    sections = ManyToManyField('SynopsisSection', through='SynopsisSectionTopic')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_topics'

    def __str__(self):
        return self.name


class SynopsisSection(Model):
    name = TextField()
    content = RichTextField()
    topics = ManyToManyField(SynopsisTopic, through='SynopsisSectionTopic')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_sections'

    def __str__(self):
        return self.name


class ClassSynopses(Model):
    corresponding_class = ForeignKey(Class, on_delete=models.CASCADE)
    description = TextField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'class_synopses'

    def __str__(self):
        return f'{self.corresponding_class}'


class ClassSynopsesSections(Model):
    section = ForeignKey(SynopsisSection, on_delete=models.CASCADE)
    class_synopsis = ForeignKey(ClassSynopses, on_delete=models.PROTECT)
    index = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'class_synopsis_sections'

    def __str__(self):
        return f'{self.section} annexed to {self.class_synopsis}.'


class SynopsisSectionTopic(Model):
    section = ForeignKey(SynopsisSection, on_delete=models.CASCADE)
    topic = ForeignKey(SynopsisTopic, on_delete=models.PROTECT)
    index = IntegerField(default=1024)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_section_topics'

    def __str__(self):
        return f'{self.section} linked to {self.topic}.'


class SynopsisSectionLog(Model):
    author = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    section = ForeignKey(SynopsisSection, on_delete=models.CASCADE)
    timestamp = DateTimeField(auto_now_add=True)

    # delta = TextField() # TODO store diffs

    def __str__(self):
        return f'{self.author} edited {self.section} @ {self.timestamp}.'


class Tag(Model):
    name = TextField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'tags'


class Article(Model):
    name = TextField(max_length=100)
    content = TextField()
    datetime = DateTimeField(default=timezone.now)
    authors = ManyToManyField(User, through='ArticleAuthors')
    tags = ManyToManyField(Tag, through='ArticleTags')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'articles'


class ArticleAuthors(Model):
    article = ForeignKey(Article, on_delete=models.CASCADE)
    author = ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'article_authors'


class ArticleComment(Model):
    article = ForeignKey(Article, on_delete=models.CASCADE)
    comment = TextField()
    datetime = DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'article_comments'


class ArticleTags(Model):
    article = ForeignKey(Article, on_delete=models.CASCADE)
    tag = ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'article_tags'


class NewsItem(Model):
    title = TextField(max_length=100)
    summary = TextField(max_length=300)
    content = TextField()
    datetime = DateTimeField(auto_now_add=True)
    edited = BooleanField(default=False)
    edit_note = TextField(null=True, blank=True, default=None)
    edit_datetime = DateTimeField(null=True, blank=True, default=None)
    author = ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='author')
    edit_author = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='edit_author')
    tags = ManyToManyField(Tag, through="NewsTags")

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'news_items'

    def __str__(self):
        return self.title


class NewsTags(Model):
    news_item = ForeignKey(NewsItem, on_delete=models.CASCADE)
    tag = ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'news_tags'


class VoteType(Model):
    type = TextField(max_length=20)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'vote_types'

    def __str__(self):
        return self.type


class NewsVote(Model):
    news_item = ForeignKey(NewsItem, on_delete=models.CASCADE)
    vote_type = ForeignKey(VoteType, on_delete=models.PROTECT)
    user = ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'news_votes'


class ArticleVote(Model):
    article = ForeignKey(Article, on_delete=models.CASCADE)
    vote_type = ForeignKey(VoteType, on_delete=models.PROTECT)
    user = ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'article_votes'


class Role(Model):
    name = TextField(max_length=30)
    is_group_admin = BooleanField(default=False)
    is_group_manager = BooleanField(default=False)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'roles'


class GroupType(Model):
    type = TextField(max_length=50)
    description = TextField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_types'

    def __str__(self):
        return self.type


class Group(Model):
    name = TextField(max_length=50)
    description = TextField()
    invite_only = BooleanField(default=True)
    type = ForeignKey(GroupType, on_delete=models.PROTECT)
    users = ManyToManyField(User, through="GroupUsers")
    roles = ManyToManyField(Role, through="GroupRoles")

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'groups'

    def __str__(self):
        return self.name


class GroupUsers(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE)
    user = ForeignKey(User, on_delete=models.CASCADE)
    role = ForeignKey(Role, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_users'


class GroupRoles(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE)
    role = ForeignKey(Role, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_roles'


class Badge(Model):
    name = TextField(max_length=30, unique=True, default=None)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'badges'


class UserBadges(Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    badge = ForeignKey(Badge, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'user_badges'


class StoreItem(Model):
    name = TextField(max_length=100)
    description = TextField()
    price = IntegerField(default=None, null=True, blank=True)
    stock = IntegerField(default=-1)
    seller = ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'store_items'

    def __str__(self):
        return '%s (%d.%02d€)' % (self.name, int(self.price / 100), self.price % 100)


class ClassifiedItem(Model):
    name = TextField(max_length=100)
    description = TextField()
    price = IntegerField()
    seller = ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'classified_items'

    def __str__(self):
        return self.name


class Comment(Model):
    author = ForeignKey(User, null=True, on_delete=models.SET_NULL)
    content = TextField(max_length=1024)
    datetime = DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'comments'


class FeedbackEntry(Model):
    title = TextField(max_length=100)
    description = TextField()
    author = ForeignKey(User, null=True, on_delete=models.SET_NULL)
    comments = ManyToManyField(Comment, through='FeedbackEntryComment')
    closed = BooleanField()
    reason = TextField(max_length=100)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'feedback_entries'


class FeedbackEntryComment(Model):
    comment = ForeignKey(Comment, on_delete=models.CASCADE)
    entry = ForeignKey(FeedbackEntry, on_delete=models.CASCADE)
    positive = BooleanField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'feedback_entry_comments'


class ChangeLog(Model):
    title = TextField(max_length=100)
    content = RichTextField()
    date = DateField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'changelogs'

    def __str__(self):
        return self.title


class Catchphrase(Model):
    phrase = TextField(max_length=100)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'catchphrases'

    def __str__(self):
        return self.phrase
