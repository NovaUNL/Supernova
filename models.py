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

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'students'

    def __str__(self):
        return str(self.user)


class StudentClipStudent(Model):  # Oh boy, naming conventions going strong with this one...
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


class Course(Model):
    name = TextField(max_length=200)
    description = TextField(max_length=4096, null=True, blank=True)
    degree = ForeignKey(Degree, on_delete=models.PROTECT)
    abbreviation = TextField(max_length=100, null=True, blank=True)
    active = BooleanField(default=True)
    clip_course = ForeignKey(ClipCourse, on_delete=models.PROTECT, related_name='crawled_course')
    main_course = ForeignKey(Area, on_delete=models.PROTECT, related_name='main_course', null=True, blank=True)
    courses = ManyToManyField(Area, through='CourseArea')
    url = TextField(max_length=256, null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'courses'

    def __str__(self):
        return self.name


class CourseArea(Model):
    course = ForeignKey(Area, on_delete=models.PROTECT)
    course_variant = ForeignKey(Course, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'course_areas'


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


class Classroom(Model):
    name = TextField(max_length=100)
    building = ForeignKey(Building, on_delete=models.CASCADE)
    clip_classroom = OneToOneField(ClipClassroom, null=True, blank=True, on_delete=models.PROTECT)
    unlocked = NullBooleanField(null=True, default=None)
    is_laboratory = BooleanField(default=False)  # TODO make type a separate entity
    is_auditorium = BooleanField(default=False)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'classrooms'
        ordering = ('building', 'name',)

    def __str__(self):
        return f"{self.building} {self.name}"

    def short_str(self):
        return f"{self.name}\n{self.building.abbreviation}"


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


class Class(Model):
    name = TextField(max_length=30)
    abbreviation = TextField(max_length=10, default='HELP')
    description = TextField(max_length=1024, null=True, blank=True)
    synopsis = ForeignKey("Synopsis", null=True, on_delete=models.SET_NULL)
    department = ForeignKey(Department, on_delete=models.PROTECT, null=True)
    clip_class = OneToOneField(ClipClass, on_delete=models.PROTECT, related_name='related_class')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'classes'

    def __str__(self):
        return self.name


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
    classroom = ForeignKey(Classroom, on_delete=models.PROTECT, null=True, blank=True)

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
    name = TextField(max_length=100)
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()
    users = ManyToManyField(User, through="EventUsers")

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'events'


class EventUsers(Model):
    event = ForeignKey(Event, on_delete=models.CASCADE)
    user = ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'event_users'


class TurnEvent(Model):
    event = OneToOneField(Event, on_delete=models.PROTECT)
    turn_instance = ForeignKey(TurnInstance, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'turn_events'


class Workshop(Model):
    name = TextField(max_length=100)
    description = TextField(max_length=4096, null=True, blank=True)
    capacity = IntegerField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'workshops'


class WorkshopEvent(Model):
    event = OneToOneField(Event, on_delete=models.PROTECT)
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


class PartyEvent(Model):
    event = OneToOneField(Event, on_delete=models.PROTECT)
    party = ForeignKey(Party, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'party_events'


class GenericEvent(Model):
    event = OneToOneField(Event, on_delete=models.PROTECT)
    name = TextField(max_length=100)
    description = TextField(max_length=4096, null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'generic_events'


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


class Synopsis(Model):
    completeness = IntegerField(default=0)
    note = TextField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopses'


class SynopsisChapter(Model):
    name = TextField()
    number = IntegerField()
    synopsis = ForeignKey(Synopsis, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_chapters'


class SynopsisChapterPart(Model):
    name = TextField()
    content = TextField()
    contentType = TextField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_chapter_parts'


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


class StoreItem(Model):
    name = TextField(max_length=30)
    description = TextField()
    price = IntegerField(default=0, null=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'store_items'

    def __str__(self):
        return '%s (%d.%02d€)' % (self.name, int(self.price / 100), self.price % 100)


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
