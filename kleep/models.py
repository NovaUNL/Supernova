from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Model, IntegerField, TextField, ForeignKey, DateTimeField, ManyToManyField, DateField, \
    BooleanField, OneToOneField, TimeField, CharField, FloatField, NullBooleanField
from ckeditor.fields import RichTextField

from clip import models as clip

KLEEP_TABLE_PREFIX = 'kleep_'
CLIPY_TABLE_PREFIX = 'clip_'


class TemporalEntity:
    first_year = IntegerField(blank=True, null=True)
    last_year = IntegerField(blank=True, null=True)

    def has_time_range(self):
        return not (self.first_year is None or self.last_year is None)


class Profile(Model):
    name = TextField()
    nickname = TextField()
    birth_date = DateField()
    user = OneToOneField(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'users'

    def __str__(self):
        return "{} ({})".format(self.nickname, self.name)


class Student(Model):
    # A student can exist without having an account
    profile = ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    number = IntegerField(null=True, blank=True)
    abbreviation = TextField(null=True, blank=True)
    course = ForeignKey('Course', on_delete=models.PROTECT)
    turns = ManyToManyField('Turn', through='TurnStudents')
    class_instances = ManyToManyField('ClassInstance', through='Enrollment')
    first_year = IntegerField(null=True, blank=True)
    last_year = IntegerField(null=True, blank=True)
    confirmed = BooleanField(default=False)
    clip_student = ForeignKey(clip.Student, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'students'

    def __str__(self):
        return str(self.profile)


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
    clip_building = OneToOneField(clip.Building, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'buildings'

    def __str__(self):
        return self.name


class Place(Model):
    name = TextField(max_length=100)
    building = ForeignKey(Building, null=True, blank=True, on_delete=models.PROTECT)
    floor = IntegerField(default=0)
    unlocked = NullBooleanField(null=True, default=None)
    clip_classroom = OneToOneField(clip.Classroom, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'places'
        ordering = ('building', 'name')

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
    clip_department = OneToOneField(clip.Department, on_delete=models.PROTECT)
    img_url = TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'departments'

    def __str__(self):
        return self.name


class Course(Model):
    name = TextField(max_length=200)
    description = TextField(max_length=4096, null=True, blank=True)
    degree = ForeignKey(clip.Degree, on_delete=models.PROTECT)
    abbreviation = TextField(max_length=100, null=True, blank=True)
    active = BooleanField(default=True)
    clip_course = ForeignKey(clip.Course, on_delete=models.PROTECT, related_name='crawled_course')
    department = ForeignKey('Department', on_delete=models.PROTECT)
    areas = ManyToManyField(Area, through='CourseArea')
    url = TextField(max_length=256, null=True, blank=True)
    curriculum = ManyToManyField('Class', through='Curriculum')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'courses'

    def __str__(self):
        return f'{self.degree.name} em {self.name}'


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
    clip_class = OneToOneField(clip.Class, on_delete=models.PROTECT, related_name='related_class')
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
    period = ForeignKey(clip.Period, on_delete=models.PROTECT)
    year = IntegerField()
    clip_class_instance = OneToOneField(clip.ClassInstance, on_delete=models.PROTECT)
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
    clip_enrollment = ForeignKey(clip.Enrollment, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'enrollments'


class Turn(Model):
    class_instance = ForeignKey(ClassInstance, on_delete=models.CASCADE)  # Eg: Analysis
    turn_type = ForeignKey(clip.TurnType, on_delete=models.PROTECT)  # Theoretical
    number = IntegerField()  # 1
    clip_turn = OneToOneField(clip.Turn, on_delete=models.PROTECT)
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
    clip_turn_instance = OneToOneField(clip.TurnInstance, on_delete=models.PROTECT)
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
    users = ManyToManyField(Profile, through='EventUsers')

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
    user = ForeignKey(Profile, on_delete=models.CASCADE)

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


class Sellable:
    price = IntegerField()

    def price_str(self):
        return '%0.2f' % (self.price / 100)


class BarDailyMenu(Sellable, Model):
    bar = ForeignKey(Bar, on_delete=models.CASCADE)
    date = DateField(auto_now_add=True)
    item = TextField(max_length=100)
    price = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'bar_daily_menus'

    def __str__(self):
        return f'{self.item}, {self.bar} ({self.date})'


class BarPrice(Sellable, Model):
    bar = ForeignKey(Bar, on_delete=models.CASCADE)
    item = TextField(max_length=100)
    price = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'bar_prices'

    def __str__(self):
        return '%s, %0.2f€ (%s)' % (self.item, self.price / 100, self.bar.service.name)


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
    abbreviation = TextField(max_length=30, null=True, blank=True)
    name = TextField(max_length=50)
    description = TextField()
    invite_only = BooleanField(default=True)
    type = ForeignKey(GroupType, on_delete=models.PROTECT, null=True, blank=True)
    public_members = BooleanField(default=False)
    members = ManyToManyField(Profile, through='GroupMembers')
    roles = ManyToManyField(Role, through='GroupRoles')
    img_url = TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'groups'

    def __str__(self):
        return self.name


class GroupMembers(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE)
    member = ForeignKey(Profile, on_delete=models.CASCADE)
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


class GroupAnnouncement(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE)
    title = TextField(max_length=256)
    announcement = TextField()
    announcer = ForeignKey(Profile, on_delete=models.PROTECT)  # TODO consider user deletion
    datetime = DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_announcement'

    def __str__(self):
        return self.title


class Conversation(Model):
    creator = ForeignKey(Profile, on_delete=models.PROTECT, related_name='creator')
    date = DateField(auto_now_add=True)
    users = ManyToManyField(Profile, through='ConversationUser')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'conversations'


class Message(Model):
    author = ForeignKey(Profile, on_delete=models.PROTECT)  # TODO consider user deletion
    datetime = DateTimeField(auto_now_add=True)
    content = TextField()
    conversation = ForeignKey(Conversation, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'messages'


# A user relation to a conversation
class ConversationUser(Model):
    conversation = ForeignKey(Conversation, on_delete=models.CASCADE)
    user = ForeignKey(Profile, on_delete=models.PROTECT)  # TODO consider user deletion
    last_read_message = ForeignKey(Message, null=True, blank=True, on_delete=models.PROTECT)


# A conversation from an outsider to a group
class GroupExternalConversation(Conversation):
    group = ForeignKey(Group, on_delete=models.PROTECT)
    user_ack = BooleanField()
    group_ack = BooleanField()
    closed = BooleanField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_external_conversations'


# A conversation within a group
class GroupInternalConversation(Conversation):
    group = ForeignKey(Group, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_internal_conversations'


class Badge(Model):
    name = TextField(max_length=30, unique=True, default=None)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'badges'


class UserBadges(Model):
    user = ForeignKey(Profile, on_delete=models.CASCADE)
    badge = ForeignKey(Badge, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'user_badges'


class Comment(Model):
    author = ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    content = TextField(max_length=1024)
    datetime = DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'comments'


class FeedbackEntry(Model):
    title = TextField(max_length=100)
    description = TextField()
    author = ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
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


class Document(Model):
    author_user = ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL, related_name='document_author')
    author_group = ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL)
    title = TextField(max_length=300)
    content = RichTextField()
    creation = DateField(auto_now_add=True)
    public = BooleanField(default=False)
    last_edition = DateTimeField(null=True, blank=True, default=None)
    last_editor = ForeignKey(Profile, null=True, blank=True, default=None, on_delete=models.SET_NULL,
                             related_name='document_editor')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'documents'

    def __str__(self):
        return f'{self.title}, {self.author_user}'


class DocumentUserPermission(Model):
    document = ForeignKey(Document, on_delete=models.CASCADE)
    user = ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'document_users'


class DocumentGroupPermission(Model):
    document = ForeignKey(Document, on_delete=models.CASCADE)
    group = ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'document_groups'
