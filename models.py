from django.db import models
from django.contrib.auth.models import User as SysUser

# CLIPy Models (Unmanaged)
CLIPY_TABLE_PREFIX = 'clip_'


class TemporalEntity:
    first_year = models.IntegerField(blank=True, null=True)
    last_year = models.IntegerField(blank=True, null=True)

    def has_time_range(self):
        return not (self.first_year is None or self.last_year is None)


class Degree(models.Model):
    id = models.IntegerField(primary_key=True)
    internal_id = models.TextField(null=True, max_length=5)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'degrees'

    def __str__(self):
        return self.name


class Period(models.Model):
    id = models.IntegerField(primary_key=True)
    part = models.IntegerField()
    parts = models.IntegerField()
    type_letter = models.TextField()
    start_month = models.IntegerField(null=True)
    end_month = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'periods'

    def __str__(self):
        return "{} out of {}({})".format(self.part, self.parts, self.type_letter)


class TurnType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(max_length=30)
    abbreviation = models.TextField(max_length=5)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_types'

    def __str__(self):
        return self.name


class ClipInstitution(TemporalEntity, models.Model):
    id = models.IntegerField(primary_key=True)
    internal_id = models.IntegerField()
    abbreviation = models.TextField(max_length=10)
    name = models.TextField(null=True, max_length=50)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'institutions'

    def __str__(self):
        return self.abbreviation


class ClipBuilding(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(max_length=30)
    institution = models.ForeignKey('ClipInstitution', on_delete=models.PROTECT, db_column='institution_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'buildings'

    def __str__(self):
        return self.name


class ClipDepartment(models.Model, TemporalEntity):
    id = models.IntegerField(primary_key=True)
    internal_id = models.TextField()
    name = models.TextField(max_length=50)
    institution = models.ForeignKey(ClipInstitution, on_delete=models.PROTECT, db_column='institution_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'departments'

    def __str__(self):
        return "{}({}, {})".format(self.name, self.internal_id, self.institution.abbreviation) + super().__str__()


class ClipClass(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(null=True)
    internal_id = models.TextField(null=True)
    department = models.ForeignKey(ClipDepartment, on_delete=models.PROTECT, db_column='department_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'classes'

    def __str__(self):
        return "{}(id:{}, dept:{})".format(self.name, self.internal_id, self.department)


class ClipClassroom(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(max_length=70)
    building = models.ForeignKey('ClipBuilding', on_delete=models.PROTECT, db_column='building_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'classrooms'

    def __str__(self):
        return "{} - {}".format(self.name, self.building.name)


class ClipTeacher(models.Model):
    __tablename__ = CLIPY_TABLE_PREFIX + 'teachers'
    id = models.IntegerField(primary_key=True)
    name = models.TextField(max_length=100)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'teachers'

    def __str__(self):
        return self.name


class ClipClassInstance(models.Model):
    id = models.IntegerField(primary_key=True)
    parent = models.ForeignKey(ClipClass, on_delete=models.PROTECT, db_column='class_id')
    period = models.ForeignKey(Period, on_delete=models.PROTECT, db_column='period_id')
    year = models.IntegerField()
    regent = models.ForeignKey(ClipTeacher, on_delete=models.PROTECT, db_column='regent_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'class_instances'

    def __str__(self):
        return "{} on period {} of {}".format(self.parent, self.period, self.year)


class ClipCourse(TemporalEntity, models.Model):
    id = models.IntegerField(primary_key=True)
    internal_id = models.IntegerField()
    name = models.TextField(max_length=70)
    abbreviation = models.TextField(null=True, max_length=15)  # TODO this unique, but only for an institution
    institution = models.ForeignKey(ClipInstitution, on_delete=models.PROTECT, db_column='institution_id')
    degree = models.ForeignKey(Degree, on_delete=models.PROTECT, db_column='degree_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'courses'

    def __str__(self):
        return ("{}(ID:{} Abbreviation:{}, Degree:{} Institution:{})".format(
            self.name, self.internal_id, self.abbreviation, self.degree, self.institution)
                + super().__str__())


class ClipStudent(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    internal_id = models.IntegerField()
    abbreviation = models.TextField(null=True, max_length=30)
    course = models.ForeignKey(ClipCourse, on_delete=models.PROTECT, db_column='course_id')
    institution = models.ForeignKey(ClipInstitution, on_delete=models.PROTECT, db_column='institution_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'students'

    def __str__(self):
        return "{} ({}, {})".format(self.name, self.internal_id, self.abbreviation)


class ClipAdmission(models.Model):
    id = models.IntegerField(primary_key=True)
    student = models.ForeignKey(ClipStudent, on_delete=models.PROTECT, db_column='student_id')
    course = models.ForeignKey(ClipCourse, on_delete=models.PROTECT, db_column='course_id')
    phase = models.IntegerField(null=True)
    year = models.IntegerField(null=True)
    option = models.IntegerField(null=True)
    state = models.TextField(null=True, max_length=50)
    check_date = models.DateTimeField()
    name = models.TextField(null=True, max_length=100)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'admissions'

    def __str__(self):
        return ("{}, admitted to {}({}) (option {}) at the phase {} of the {} contest. {} as of {}".format(
            (self.student.name if self.student_id is not None else self.name),
            self.course.abbreviation, self.course_id, self.option, self.phase, self.year, self.state,
            self.check_date))


class ClipEnrollment(models.Model):
    id = models.IntegerField(primary_key=True)
    student = models.ForeignKey(ClipStudent, on_delete=models.PROTECT, db_column='student_id')
    class_instance = models.ForeignKey(ClipClassInstance, on_delete=models.PROTECT, db_column='class_instance_id')
    attempt = models.IntegerField(null=True)
    student_year = models.IntegerField(null=True)
    statutes = models.TextField(blank=True, null=True, max_length=20)
    observation = models.TextField(blank=True, null=True, max_length=30)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'enrollments'

    def __str__(self):
        return "{} enrolled to {}, attempt:{}, student year:{}, statutes:{}, obs:{}".format(
            self.student, self.class_instance, self.attempt, self.student_year, self.statutes, self.observation)


class ClipTurn(models.Model):
    id = models.IntegerField(primary_key=True)
    number = models.IntegerField()
    type = models.ForeignKey(TurnType, on_delete=models.PROTECT, db_column='type_id')
    class_instance = models.ForeignKey(ClipClassInstance, on_delete=models.PROTECT, db_column='class_instance_id')
    minutes = models.IntegerField(null=True)
    enrolled = models.IntegerField(null=True)
    capacity = models.IntegerField(null=True)
    routes = models.TextField(blank=True, null=True, max_length=30)
    restrictions = models.TextField(blank=True, null=True, max_length=30)
    state = models.TextField(blank=True, null=True, max_length=30)
    students = models.ManyToManyField(ClipStudent, through='ClipTurnStudent')
    teachers = models.ManyToManyField(ClipTeacher, through='ClipTurnTeacher')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turns'

    def __str__(self):
        return "turn {}.{} of {} {}/{} students, {} hours, {} routes, state={}, teachers={}".format(
            self.type, self.number, self.class_instance, self.enrolled, self.capacity,
            self.minutes / 60, self.routes, self.state, len(self.teachers))


class ClipTurnInstance(models.Model):
    id = models.IntegerField(primary_key=True)
    turn = models.ForeignKey(ClipTurn, on_delete=models.PROTECT, db_column='turn_id')
    start = models.IntegerField()
    end = models.IntegerField(null=True)
    weekday = models.IntegerField(null=True)
    classroom = models.ForeignKey(ClipClassroom, on_delete=models.PROTECT, db_column='classroom_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_students'


class ClipTurnTeacher(models.Model):
    turn = models.ForeignKey(ClipTurn, on_delete=models.PROTECT)
    teacher = models.ForeignKey(ClipTeacher, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_students'


class ClipTurnStudent(models.Model):
    turn = models.ForeignKey(ClipTurn, on_delete=models.PROTECT, db_column='turn_id')
    student = models.ForeignKey(ClipStudent, on_delete=models.PROTECT, db_column='student_id')

    class Meta:
        managed = False
        db_table = 'ClipTurnStudents'


# MANAGED MODELS

class User(models.Model):
    name = models.TextField()
    nickname = models.TextField()
    birth_date = models.DateField()
    sys_user = models.ForeignKey(SysUser, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "{} ({})".format(self.nickname, self.name)

    class Meta:
        managed = True
        db_table = 'Users'


class Student(User):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    crawled_students = models.ManyToManyField(ClipStudent, through='StudentClipStudent')

    class Meta:
        managed = True
        db_table = 'Students'


class StudentClipStudent(models.Model):  # Oh boy, naming conventions going strong with this one...
    clip_student = models.ForeignKey(ClipStudent, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'StudentClipStudents'


class Course(models.Model):
    courses = models.ManyToManyField(ClipCourse, through='CourseClipCourse')

    class Meta:
        managed = True
        db_table = 'Courses'


class CourseClipCourse(models.Model):
    clip_course = models.ForeignKey(ClipCourse, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'CourseClipCourses'


class Building(models.Model):
    name = models.TextField(max_length=30, unique=True)
    map_tag = models.TextField(max_length=20)

    class Meta:
        managed = True
        db_table = 'Buildings'

    def __str__(self):
        return self.name


class BuildingUsage(models.Model):
    usage = models.TextField(max_length=50)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    url = models.TextField(max_length=100)

    class Meta:
        managed = True
        db_table = 'BuildingUsages'


class Service(models.Model):
    name = models.TextField(max_length=30)
    building = models.ForeignKey(Building, null=True, on_delete=models.CASCADE)
    map_tag = models.TextField(max_length=15)

    class Meta:
        managed = True
        db_table = 'Services'


class Bar(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'Bars'


class Synopsis(models.Model):
    completeness = models.IntegerField(default=0)
    note = models.TextField()

    class Meta:
        managed = True
        db_table = 'Synopses'


class SynopsisChapter(models.Model):
    name = models.TextField()
    number = models.IntegerField()
    synopsis = models.ForeignKey(Synopsis, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'SynopsisChapters'


class SynopsisChapterPart(models.Model):
    name = models.TextField()
    content = models.TextField()
    contentType = models.TextField()

    class Meta:
        managed = True
        db_table = 'SynopsisChapterParts'


class Class(models.Model):
    name = models.TextField(max_length=30)
    synopsis = models.ForeignKey(Synopsis, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'Classes'


class Tag(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'Tags'


class Article(models.Model):
    name = models.TextField(max_length=100)
    content = models.TextField()
    datetime = models.DateTimeField()  # TODO set default
    authors = models.ManyToManyField(User, through='ArticleAuthors')
    tags = models.ManyToManyField(Tag, through='ArticleTags')

    class Meta:
        managed = True
        db_table = 'Articles'


class ArticleAuthors(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'ArticleAuthors'


class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment = models.TextField()
    datetime = models.DateTimeField()  # TODO set default

    class Meta:
        managed = True
        db_table = 'ArticleComments'


class ArticleTags(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'ArticleTags'


class EventType(models.Model):
    type = models.TextField(max_length=30)

    class Meta:
        managed = True
        db_table = 'EventTypes'


class Event(models.Model):
    name = models.TextField()
    description = models.TextField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    users = models.ManyToManyField(User, through="EventUsers")
    types = models.ManyToManyField(EventType, through="EventTypes")

    class Meta:
        managed = True
        db_table = 'Events'


class EventTypes(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    type = models.ForeignKey(EventType, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = 'EventEventTypes'


class EventRelationship(models.Model):  # "Going", "Not Going", "Don't Know", something else?
    relationship = models.TextField(max_length=15)

    class Meta:
        managed = True
        db_table = 'EventRelationships'

    def __str__(self):
        return self.relationship


class EventUsers(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    relationship = models.ForeignKey(EventRelationship, on_delete=models.PROTECT)
    changed = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'EventUsers'


class StoreItem(models.Model):
    name = models.TextField(max_length=30)
    description = models.TextField()
    price = models.IntegerField(default=0, null=True)

    class Meta:
        managed = True
        db_table = 'StoreItems'

    def __str__(self):
        return '%s (%d.%02d€)' % (self.name, int(self.price / 100), self.price % 100)


class NewsItem(models.Model):
    title = models.TextField(max_length=100)
    summary = models.TextField(max_length=300)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, through="NewsTags")

    class Meta:
        managed = True
        db_table = 'NewsItems'


class NewsTags(models.Model):
    news_item = models.ForeignKey(NewsItem, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'NewsTags'


class VoteType(models.Model):
    type = models.TextField(max_length=20)

    class Meta:
        managed = True
        db_table = 'VoteTypes'

    def __str__(self):
        return self.type


class NewsVote(models.Model):
    news_item = models.ForeignKey(NewsItem, on_delete=models.CASCADE)
    vote_type = models.ForeignKey(VoteType, on_delete=models.PROTECT)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'NewsVotes'


class ArticleVote(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    vote_type = models.ForeignKey(VoteType, on_delete=models.PROTECT)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'ArticleVotes'


class Role(models.Model):
    name = models.TextField(max_length=30)
    is_group_admin = models.BooleanField(default=False)
    is_group_manager = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'Roles'


class GroupType(models.Model):
    type = models.TextField(max_length=50)
    description = models.TextField()

    class Meta:
        managed = True
        db_table = 'GroupTypes'


class Group(models.Model):
    name = models.TextField(max_length=50)
    description = models.TextField()
    invite_only = models.BooleanField(default=True)
    type = models.ForeignKey(GroupType, on_delete=models.PROTECT)
    users = models.ManyToManyField(User, through="GroupUsers")
    roles = models.ManyToManyField(Role, through="GroupRoles")

    class Meta:
        managed = True
        db_table = 'Groups'


class GroupUsers(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = 'GroupUsers'


class GroupRoles(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = 'GroupRoles'


class Badge(models.Model):
    pass
