import logging
import traceback
from datetime import datetime, timedelta

import reversion
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models as djm
from django.contrib.gis.db import models as gis
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, F
from django.urls import reverse
from django.utils import timezone
from imagekit.models import ImageSpecField
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from pilkit.processors import SmartResize, ResizeToFit
from polymorphic.models import PolymorphicModel

from feedback import models as feedback
from scrapper import files
from . import choice_types as ctypes

logger = logging.getLogger(__name__)


class Importable(djm.Model):
    """Objects which were imported from other supernova-alike systems trough some driver."""
    #: The ID for this object in an external system (its primary key)
    external_id = djm.IntegerField(null=True, blank=True, unique=True, db_index=True)
    #: The item internal ID its origin (not in the driver).
    # Usually the same as external_id, but for some things can be something else
    iid = djm.CharField(null=True, blank=True, max_length=64)
    #: The last time this object was updated from its external source
    external_update = djm.DateTimeField(null=True, blank=True)
    #: Whether this object should be updated
    frozen = djm.BooleanField(default=False)
    #: Equivalence to other imported object
    same_as = djm.ForeignKey('self', null=True, blank=True, on_delete=djm.SET_NULL)
    #: Flag telling that this object was possibly deleted yet it is unsure
    disappeared = djm.BooleanField(default=False)
    #: Additional external data that doesn't otherwise fit the model
    external_data = djm.JSONField(default=dict, blank=True, null=True)

    class Meta:
        abstract = True


class CachedEntity(djm.Model):
    """ Aid meta class for entities(or children) which present last_modified headers """
    #: Last update timestamp
    last_save = djm.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PeriodInstance(djm.Model):
    """An instance of time where class occurs"""
    #: The type of period
    type = djm.IntegerField(choices=ctypes.Period.CHOICES)
    #: Academic year
    year = djm.IntegerField()
    #: Date on which the period started
    date_from = djm.DateField(null=True, blank=True)
    #: Date on which the period ended
    date_to = djm.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('type', 'year')
        ordering = ('year', 'type')

    def __str__(self):
        return f"{self.get_type_display()} - {self.year-1}/{self.year} ({self.date_from} - {self.date_to})"


@reversion.register()
class Student(Importable, CachedEntity):
    """
    | A student instance.
    | Each user can have multiple instances if the user enrolled multiple times to multiple courses.
    """
    #: Full teacher name (eventually redundant, useful for registrations)
    name = djm.TextField(max_length=200, null=True)
    #: User this student is associated with
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=djm.CASCADE, related_name='students')
    #: The public number which identifies this student
    number = djm.IntegerField(null=True, blank=True, unique=True, db_index=True)
    #: The public textual abbreviation which identifies this student
    abbreviation = djm.CharField(null=True, blank=True, max_length=64, db_index=True)
    #: This student's course
    course = djm.ForeignKey('Course', on_delete=djm.PROTECT, related_name='students', null=True, blank=True)
    #: Shifts this student is enrolled to
    shifts = djm.ManyToManyField('Shift', through='ShiftStudents')
    #: Classes this student is enrolled to
    class_instances = djm.ManyToManyField('ClassInstance', through='Enrollment')
    #: Grade this student obtained upon finishing his course
    graduation_grade = djm.IntegerField(null=True, blank=True, default=None)
    # Cached fields
    #: | Cache field which stores the current year of this student
    #: | (years being measured with (ECTS-36)/60 + 1)
    year = djm.IntegerField(null=True, blank=True)
    #: Cache field which stores the first year on which this student was seen as active
    first_year = djm.IntegerField(null=True, blank=True)
    #: Cache field which stores the last year on which this student was seen as active
    last_year = djm.IntegerField(null=True, blank=True)
    #: Number of ECTS this student has cumulated
    credits = djm.IntegerField(null=True, blank=True)
    #: Number of ECTS this student has cumulated
    avg_grade = djm.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        if self.user:
            return f'{self.number} - {self.abbreviation} ({self.user})'
        return f'{self.number} - {self.abbreviation}'

    def get_absolute_url(self):
        return reverse('college:student', args=[self.id])

    def update_progress_info(self):
        years = list(self.class_instances.distinct('year').values_list('year', flat=True))
        if len(years) > 0:
            first_year = min(years)
            last_year = max(years)
            changed = False
            if first_year != self.first_year:
                logger.warning(f'First year changed from {self.first_year} to {first_year}')
                self.first_year = first_year
                changed = True
            if last_year != self.last_year:
                logger.warning(f'Last year changed from {self.last_year} to {last_year}')
                self.last_year = last_year
                changed = True

            grade_info = self.enrollments \
                .filter(approved=True) \
                .all() \
                .aggregate(credit_grade=Sum(F('grade') * F('class_instance__parent__credits')),
                           credit_count=Sum('class_instance__parent__credits'))
            credit_grade = grade_info['credit_grade']
            credit_count = grade_info['credit_count']
            if credit_grade and credit_count:
                avg_grade = credit_grade / credit_count
                if self.credits != credit_count:
                    self.credits = credit_count
                    changed = True
                if self.avg_grade != avg_grade:
                    self.avg_grade = avg_grade
                    changed = True
            if changed:
                self.save(update_fields=['credits', 'avg_grade', 'first_year', 'last_year'])

    @property
    def ects(self):
        if self.credits:
            return self.credits // 2


def building_pic_path(building, filename):
    return f'c/b/{building.id}/pic.{filename.split(".")[-1].lower()}'


@reversion.register()
class Building(Importable, CachedEntity):
    """A physical building withing the campus"""
    #: Full name
    name = djm.CharField(max_length=32, unique=True)
    #: Abbreviated name
    abbreviation = djm.CharField(max_length=16, unique=True, null=True, db_index=True)
    #: Tag in the campus map
    map_tag = djm.CharField(max_length=20, unique=True)
    #: Geographical center
    location = gis.PointField(geography=True, null=True)
    #:  Picture illustrating this building
    picture = djm.ImageField(upload_to=building_pic_path, null=True, blank=True)
    picture_thumbnail = ImageSpecField(
        source='picture',
        processors=[ResizeToFit(*settings.THUMBNAIL_SIZE)],
        format='JPEG',
        options={'quality': settings.MEDIUM_QUALITY})
    picture_cover = ImageSpecField(
        source='picture',
        processors=[ResizeToFit(*settings.COVER_SIZE)],
        format='JPEG',
        options={'quality': settings.HIGH_QUALITY})

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('college:building', args=[self.id])


def department_pic_path(department, filename):
    return f'c/d/{department.id}/pic.{filename.split(".")[-1].lower()}'


@reversion.register()
class Department(Importable, CachedEntity):
    """An (official) department"""
    #: Full name of the department
    name = djm.CharField(max_length=128)
    #: Verbose description of the department role and activities.
    description = MarkdownxField(null=True, blank=True)
    #: Headquarters building
    building = djm.ForeignKey(Building, on_delete=djm.PROTECT, null=True, blank=True, related_name='departments')
    #: Flag telling whether the department still exists
    extinguished = djm.BooleanField(default=True)
    #: Picture illustrating this department
    picture = djm.ImageField(upload_to=department_pic_path, null=True, blank=True)
    picture_thumbnail = ImageSpecField(
        source='picture',
        processors=[SmartResize(*settings.THUMBNAIL_SIZE)],
        format='JPEG',
        options={'quality': settings.MEDIUM_QUALITY})
    #: URL to this departments's official page
    url = djm.URLField(max_length=256, null=True, blank=True)
    #: Phone number in the format +country number,extension
    phone = djm.CharField(max_length=20, null=True, blank=True)
    #: This department's general email address
    email = djm.EmailField(null=True, blank=True)
    #: This department's president
    president = djm.ForeignKey(
        'Teacher',
        null=True,
        blank=True,
        on_delete=djm.PROTECT,
        related_name='presided_departments')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('college:department', args=[self.id])


def place_pic_path(room, filename):
    return f'c/b/{room.id}/pic.{filename.split(".")[-1].lower()}'


class Place(CachedEntity):
    """
    A generic geographical place
    TODO: Change to include building
    """
    #: Name of the place
    name = djm.CharField(max_length=128)
    #: Building it is located at
    building = djm.ForeignKey(Building, null=True, blank=True, on_delete=djm.PROTECT, related_name='places')
    #: Building floor where it is located
    floor = djm.IntegerField(default=0)
    #: Whether it is unlocked to unidentified personnel.
    unlocked = djm.BooleanField(null=True, default=None)
    #: Geographic location of the place
    location = gis.PointField(geography=True, null=True, blank=True)
    #: List of features associated with this place (risk of explosion, special clothing, ...)
    features = djm.ManyToManyField('PlaceFeature', blank=True)
    #: Picture illustrating this place
    picture = djm.ImageField(upload_to=place_pic_path, null=True, blank=True)
    picture_cover = ImageSpecField(
        source='picture',
        processors=[SmartResize(*settings.COVER_SIZE)],
        format='JPEG',
        options={'quality': settings.MEDIUM_QUALITY})

    def __str__(self):
        return f'{self.name} ({self.building})'

    def short_str(self):
        return f"{self.name} ({self.building.abbreviation})"


def feature_pic_path(feature, filename):
    return f'c/f/{feature.id}.{filename.split(".")[-1].lower()}'


class PlaceFeature(djm.Model):
    name = djm.CharField(max_length=100)
    description = djm.TextField()
    icon = djm.FileField(upload_to=feature_pic_path)

    def __str__(self):
        return self.name


@reversion.register()
class Room(Place, Importable):
    """A physical room within the campus"""
    #: Department that manages this room
    department = djm.ForeignKey(Department, on_delete=djm.PROTECT, related_name='rooms', null=True, blank=True)
    #: Person capacity
    capacity = djm.IntegerField(null=True, blank=True)
    #: The door number (ignoring the floor number)
    door_number = djm.IntegerField(null=True, blank=True)
    #: Type of room (enumeration)
    type = djm.IntegerField(choices=ctypes.RoomType.CHOICES, default=0)
    #: Verbose description for this room
    description = djm.TextField(null=True, blank=True)
    #: Verbose description of equipment in this room
    equipment = djm.TextField(null=True, blank=True)
    #: Whether the room still exists as referred to by this object
    extinguished = djm.BooleanField(default=False)

    class Meta:
        ordering = ('floor', 'door_number', 'name')
        # unique_together = ('name', 'building', 'type') inheritance forbids this

    def __str__(self):
        return f'{self.building.abbreviation} {self.name}'

    def short_str(self):
        return f'{self.building.abbreviation} {self.name}'

    def long_str(self):
        return f'{self.building.name}, {self.get_type_display()} {self.name}'

    @property
    def short_schedule_str(self):
        return f'{ctypes.RoomType.ABBREVIATIONS[self.type]} {self.name}'

    def schedule_str(self):
        return f'{self.building.abbreviation}, {self.get_type_display()} {self.name}'

    def get_absolute_url(self):
        return reverse('college:room', args=[self.id])


@reversion.register()
class Course(Importable, CachedEntity):
    """A course which is associated with a recognizable degree."""
    #: Course name
    name = djm.CharField(max_length=256)
    #: Abbreviation of the course name
    abbreviation = djm.CharField(max_length=128, null=True, blank=True)
    #: Description of the course
    description = MarkdownxField(null=True, blank=True)
    #: Conferred degree
    degree = djm.IntegerField(choices=ctypes.Degree.CHOICES)
    #: Whether the course is actively happening
    active = djm.BooleanField(default=False)
    #: Department that manages this course
    department = djm.ForeignKey('Department', null=True, blank=True, on_delete=djm.PROTECT, related_name='courses')
    #: The current de facto curriculum for this course
    curriculum = djm.ForeignKey('Curriculum', null=True, blank=True, on_delete=djm.PROTECT, related_name='courses')
    #: Teacher which coordinates this course
    coordinator = djm.ForeignKey(
        'Teacher',
        null=True,
        blank=True,
        on_delete=djm.PROTECT,
        related_name='coordinated_courses')
    #: URL to this course's official page
    url = djm.URLField(max_length=256, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{ctypes.Degree.name(self.degree)} em {self.name}'

    def get_absolute_url(self):
        return reverse('college:course', args=[self.id])

    @property
    def description_html(self):
        return markdownify(self.description)


@reversion.register()
class Class(Importable, CachedEntity):
    """A class with is taught, usually once or twice a year. Abstract concept without temporal presence"""
    #: Name of the class
    name = djm.CharField(max_length=256)
    #: Abbreviation for this class
    abbreviation = djm.CharField(max_length=16, default='---')
    #: Verbose description of the class
    description = MarkdownxField(null=True, blank=True)
    #: ECTS awarded by this class (2 credits = 1 ECTS)
    credits = djm.IntegerField(null=True, blank=True)
    #: Whether this class still exists
    extinguished = djm.BooleanField(default=False)
    #: Department that currently lectures this class (Cached attribute)
    department = djm.ForeignKey(Department, on_delete=djm.PROTECT, null=True, related_name='classes')
    #: URL to this class's official page
    url = djm.URLField(max_length=256, null=True, blank=True)
    # Cached
    #: The average grade in this instance
    avg_grade = djm.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'classes'

    def __str__(self):
        return f"{self.name} ({self.iid})"

    @property
    def title(self):
        return self.name

    @property
    def ects(self):
        return self.credits / 2

    @property
    def description_html(self):
        return markdownify(self.description)

    def get_absolute_url(self):
        return reverse('college:class', args=[self.id])


@reversion.register()
class ClassInstance(Importable, CachedEntity):
    """An instance of a class with an associated point in time"""
    #: Class this refers to
    parent = djm.ForeignKey(Class, on_delete=djm.PROTECT, related_name='instances')
    #: Department this instance belonged to
    department = djm.ForeignKey(Department, null=True, on_delete=djm.PROTECT, related_name='class_instances')
    #: Period this happened on (enumeration)
    period = djm.IntegerField(choices=ctypes.Period.CHOICES)
    #: Period this happened on (concrete instance)
    period_instance = djm.ForeignKey(PeriodInstance, null=True, blank=True, on_delete=djm.SET_NULL)
    #: Date on which the instance started (overrides the period)
    date_from = djm.DateField(null=True, blank=True)
    #: Date on which the instance ended (overrides the period)
    date_to = djm.DateField(null=True, blank=True)
    #: Year of lecturing
    year = djm.IntegerField()
    #: Enrolled students
    students = djm.ManyToManyField(Student, through='Enrollment')
    #: Main teacher in this class instance.
    regent = djm.ForeignKey('Teacher', null=True, blank=True, on_delete=djm.PROTECT, related_name='ruled_classes')
    #: Misc information associated to this class
    information = djm.JSONField(encoder=DjangoJSONEncoder)
    #: Maximum visibility
    visibility = djm.IntegerField(choices=ctypes.FileVisibility.CHOICES, default=ctypes.FileVisibility.STUDENTS)
    #: Reviews that are linked to this object
    reviews = GenericRelation(feedback.Review, related_query_name='class_instance')
    # Cached
    #: The average grade in this instance
    avg_grade = djm.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ['parent', 'period', 'year']

    def __str__(self):
        return f"{self.parent.abbreviation}, {self.short_occasion}"

    @property
    def short_str(self):
        return f"{self.parent.name}, {self.short_occasion}"

    @property
    def full_str(self):
        return f"{self.parent.name}, {self.get_period_display()} de {self.year}"

    @property
    def occasion(self):
        return f'{self.get_period_display()}, {self.year - 1}/{self.year}'

    @property
    def short_occasion(self):
        if self.year > 2000:
            return f'{ctypes.Period.SHORT_CHOICES[self.period - 1]} {self.year - 2001}/{self.year - 2000}'
        else:
            return f'{ctypes.Period.SHORT_CHOICES[self.period - 1]} {self.year - 1901}/{self.year - 1900}'

    def get_absolute_url(self):
        return reverse('college:class_instance', args=[self.id])


@reversion.register()
class ClassInstanceEvent(Importable):
    #: Class instance where this event happens
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.CASCADE, related_name='events')
    #: Date on which the event happened/will happen
    date = djm.DateField()
    #: Time at which the event started/will start
    time = djm.TimeField(null=True, blank=True)
    #: Duration of the event
    duration = djm.IntegerField(null=True, blank=True)
    #: Event type (eg. test, exam, trip, work, ...)
    type = djm.IntegerField(choices=ctypes.EventType.CHOICES, null=True)
    #: Choice between continuous, recourse and special seasons.
    season = djm.IntegerField(choices=ctypes.EventSeason.CHOICES, null=True)
    #: Textual information
    info = djm.TextField(null=True, blank=True)

    def __str__(self):
        if self.type == ctypes.EventType.TEST:
            return f'Teste de {self.class_instance.parent.abbreviation} ({self.get_season_display()})'
        elif self.type == ctypes.EventType.EXAM:
            return f'Exame de {self.class_instance.parent.abbreviation} ({self.get_season_display()})'
        elif self.type == ctypes.EventType.DISCUSSION:
            return f'Discussão de {self.class_instance.parent.abbreviation}'
        elif self.type == ctypes.EventType.PROJECT_DELIVERY:
            return f'Entrega de {self.class_instance.parent.abbreviation}'
        elif self.type == ctypes.EventType.TALK:
            return f'Palestra em {self.class_instance.parent.abbreviation}'
        elif self.type == ctypes.EventType.FIELD_TRIP:
            return f'Visita, {self.class_instance.parent.abbreviation}'
        elif self.type == ctypes.EventType.ADDITIONAL_CLASS:
            return f'Aula extra, {self.class_instance.parent.abbreviation}'
        else:
            if (self.info):
                info = self.info if (len(self.info) < 30) else self.info[:27] + "..."
            else:
                info = "Desconhecido"
            return f'{self.class_instance.parent.abbreviation}: {info}'

    @property
    def to_time(self):
        delta = timedelta(minutes=self.duration)
        return (datetime.combine(datetime.today(), self.time) + delta).time()

    @property
    def datetime_str(self):
        return datetime.combine(self.date, self.time).isoformat() if self.time else self.date.isoformat()


@reversion.register()
class Enrollment(Importable):
    """An enrollment of a student to a class"""
    #: Enrolled student
    student = djm.ForeignKey(Student, on_delete=djm.CASCADE, related_name='enrollments')
    #: Class of enrollment
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.CASCADE, related_name='enrollments')
    #: Whether the student got attendance
    attendance = djm.BooleanField(null=True)
    #: The date on which the attendance has been assigned
    attendance_date = djm.DateField(null=True, blank=True)
    #: The grade that this enrollment obtained during the normal season
    normal_grade = djm.IntegerField(null=True, blank=True)
    #: The date on which the normal season grade has been assigned
    normal_grade_date = djm.DateField(null=True, blank=True)
    #: The grade that this enrollment obtained during the recourse season
    recourse_grade = djm.IntegerField(null=True, blank=True)
    #: The date on which the recourse season grade has been assigned
    recourse_grade_date = djm.DateField(null=True, blank=True)
    #: The grade that this enrollment obtained during the special season
    special_grade = djm.IntegerField(null=True, blank=True)
    #: The date on which the special season grade has been assigned
    special_grade_date = djm.DateField(null=True, blank=True)
    #: The grade that this enrollment obtained on an auto-proposed improvement
    improvement_grade = djm.IntegerField(null=True, blank=True)
    #: The date on which the improved grade has been assigned
    improvement_grade_date = djm.DateField(null=True, blank=True)
    # Cached fields
    #: Whether this enrollment lead to an approval
    approved = djm.BooleanField(null=True, blank=True)
    #: Conclusion grade
    grade = djm.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'class_instance']

    def __str__(self):
        return f'{self.student} to {self.class_instance}'


class Shift(Importable):
    """Abstract concept of a shift, without temporal presence"""
    #: Class that this shift lectures
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.CASCADE, related_name='shifts')  # Eg: Analysis
    #: Type of shift (enumeration)
    shift_type = djm.IntegerField(choices=ctypes.ShiftType.CHOICES)  # Theoretical, Practical, ...
    #: Shift index
    number = djm.IntegerField()  # 1
    #: Required attendance
    required = djm.BooleanField(default=True)  # Optional attendance
    #: Enrolled students
    students = djm.ManyToManyField(Student, through='ShiftStudents')
    #: Associated teachers
    teachers = djm.ManyToManyField('Teacher', related_name='shifts')

    class Meta:
        unique_together = ['class_instance', 'shift_type', 'number']

    def __str__(self):
        return f"{self.class_instance} {ctypes.ShiftType.abbreviation(self.shift_type)}{self.number}"

    @property
    def type_abbreviation(self):
        return ctypes.ShiftType.abbreviation(self.shift_type)

    @property
    def short_abbreviation(self):
        return f"{self.type_abbreviation}{self.number}"

    @property
    def long_abbreviation(self):
        return f"{self.get_shift_type_display()} {self.number}"

    def get_absolute_url(self):
        return reverse('college:class_instance_shift', args=[self.class_instance_id, self.id])


class ShiftStudents(djm.Model):
    shift = djm.ForeignKey(Shift, on_delete=djm.CASCADE)
    student = djm.ForeignKey(Student, on_delete=djm.CASCADE)

    class Meta:
        verbose_name_plural = 'shift students'

    def __str__(self):
        return f'{self.student} enrolled to shift {self.shift}'


class ShiftInstance(Importable):
    """A physical presence of a Shift"""
    #:
    shift = djm.ForeignKey(Shift, on_delete=djm.CASCADE, related_name='instances')  # Eg: Theoretical 1
    #: | Whether this is a recurring shift
    #: | Recurring shifts always happen at a given weekday and hour, lasting for k minutes
    recurring = djm.BooleanField(default=True)
    #: Weekday this happens on, with the index 0 being Monday
    weekday = djm.IntegerField(null=True, blank=True, choices=ctypes.WEEKDAY_CHOICES)  # 0 - Monday
    #: Temporal offset in minutes from the midnight until the start of this shift (8*60+30 = 8:30 AM)
    start = djm.IntegerField(null=True, blank=True)
    #: Duration in minutes
    duration = djm.IntegerField(null=True, blank=True)
    # Room where the shift instance happens
    room = djm.ForeignKey(Room, on_delete=djm.PROTECT, null=True, blank=True, related_name='shift_instances')

    class Meta:
        ordering = ['weekday', 'start']

    def __str__(self):
        return f"{self.shift}, d{self.weekday}, {self.minutes_to_str(self.start)}"

    def get_absolute_url(self):
        return reverse('college:class_instance_shift', args=[self.shift_id, self.id])

    def intersects(self, shift_instance):
        # Same weekday AND A starts before B ends and B starts before A ends
        return self.weekday == shift_instance.weekday and \
               self.start < shift_instance.start + shift_instance.duration and \
               shift_instance.start < self.start + self.duration

    @property
    def weekday_pt(self):
        return ctypes.WEEKDAY_CHOICES[self.weekday][1]

    @property
    def start_str(self):
        return self.minutes_to_str(self.start)

    @property
    def end(self):
        return self.start + self.duration

    @property
    def end_str(self):
        return self.minutes_to_str(self.start + self.duration)

    @property
    def happening(self):
        now = datetime.now()
        if not (self.shift.class_instance.year == settings.COLLEGE_YEAR
                and self.shift.class_instance.period == settings.COLLEGE_PERIOD):
            return False

        # same weekday and within current time interval
        return self.weekday == now.isoweekday() and self.start < now.hour * 60 + now.min < self.start + self.duration

    @property
    def title(self):
        return f"{self.shift.get_shift_type_display()} {self.shift.class_instance.parent.abbreviation}"

    @property
    def short_title(self):
        return f"{self.shift.type_abbreviation} {self.shift.class_instance.parent.abbreviation}"

    @property
    def weekday_as_arr(self):
        # Meant to aid fullcalendar, weekday shifted
        return None if self.weekday is None else [(self.weekday + 1) % 7]

    @staticmethod
    def minutes_to_str(minutes):
        return "%02d:%02d" % (minutes // 60, minutes % 60)


class TeacherRank(djm.Model):
    #: The name of this rank
    name = djm.CharField(max_length=32)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


def teacher_pic_path(teacher, filename):
    return f'c/t/{teacher.id}/pic.{filename.split(".")[-1].lower()}'


@reversion.register()
class Teacher(Importable, CachedEntity):
    """
    | A person who teaches or investigates.
    | Note that there is an intersection between students and teachers. A student might become a teacher.
    """
    #: Full teacher name (eventually redundant, useful for registrations)
    name = djm.TextField(max_length=200, db_index=True)
    #: This teacher's rank
    rank = djm.ForeignKey(TeacherRank, on_delete=djm.PROTECT, null=True, blank=True)
    #: Departments this teacher has worked for
    departments = djm.ManyToManyField(Department, related_name="teachers")
    #: User this teacher is associated with
    user = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=djm.CASCADE,
        related_name='teachers')
    # Cached fields
    #: Cache field which stores the last year on which this teacher was seen as active
    first_year = djm.IntegerField(null=True, blank=True)
    #: Cache field which stores the last year on which this teacher was seen as active
    last_year = djm.IntegerField(null=True, blank=True)
    #: The textual abbreviation which identifies this teacher (speculated)
    abbreviation = djm.CharField(null=True, blank=True, max_length=64, db_index=True)
    #: URL to this teacher's official page
    url = djm.URLField(max_length=256, null=True, blank=True)
    #: This teacher's email
    email = djm.EmailField(max_length=256, null=True, blank=True)
    #: Phone number in the format +country number,extension
    phone = djm.CharField(max_length=20, null=True, blank=True)
    #:  A picture of this teacher
    picture = djm.ImageField(upload_to=teacher_pic_path, null=True, blank=True)
    picture_thumbnail = ImageSpecField(
        source='picture',
        processors=[SmartResize(*settings.MEDIUM_ICON_SIZE)],
        format='JPEG',
        options={'quality': settings.MEDIUM_QUALITY})
    #:  The room that a teacher occupies
    room = djm.ForeignKey(Room, null=True, blank=True, on_delete=djm.PROTECT, related_name='teachers')
    #: Reviews that are linked to this object
    reviews = GenericRelation(feedback.Review)
    #: The consent this teacher gave for uploaded files
    file_consent = djm.IntegerField(
        choices=ctypes.FileVisibility.CHOICES,
        default=None,
        null=True,
        blank=True)

    def __str__(self):
        return f"{self.name} ({self.iid})"

    @property
    def short_name(self):
        name_parts = self.name.split(" ")
        return "%s %s" % (name_parts[0], name_parts[-1]) if len(name_parts) > 1 else self.name

    def update_yearspan(self):
        years = list(self.shifts.distinct('class_instance__year').values_list('class_instance__year', flat=True))
        if len(years) > 0:
            first_year = min(years)
            last_year = max(years)
            changed = False
            if first_year != self.first_year:
                logger.warning(f'First year changed from {self.first_year} to {first_year}')
                self.first_year = first_year
                changed = True
            if last_year != self.last_year:
                logger.warning(f'Last year changed from {self.last_year} to {last_year}')
                self.last_year = last_year
                changed = True
            if changed:
                self.save(update_fields=['first_year', 'last_year'])

    def calculate_abbreviation(self):
        if self.email:
            self.abbreviation = self.email.split('@')[0]

    def get_absolute_url(self):
        return reverse('college:teacher', args=[self.id])

    @property
    def thumbnail_or_default(self):
        if self.picture:
            return self.picture_thumbnail.url


def file_upload_path(file, _):
    return f'file/{file.hash}'


PREVIEWABLE_MIMES = {
    'application/pdf',
}


@reversion.register()
class File(Importable):
    """A file in the filesystem"""
    #: File SHA1 hash
    hash = djm.CharField(max_length=40, primary_key=True)
    #: File size in (kilo)?bytes
    size = djm.IntegerField()
    #: File mimetype
    mime = djm.CharField(null=True, max_length=256)
    #: Name of the first upload
    name = djm.CharField(null=True, max_length=256)
    #: Extension as of the first upload
    extension = djm.CharField(null=True, max_length=16)
    #: Whether the file is managed externally
    external = djm.BooleanField(default=False)
    #: License of the file being shared
    license = djm.IntegerField(
        choices=ctypes.FileLicense.CHOICES,
        blank=True,
        null=True,
        default=ctypes.FileLicense.RIGHTS_RESERVED)
    #: License name string (for the unlisted licenses)
    license_str = djm.CharField(max_length=256, blank=True, null=True, default=None)
    #: User who uploaded the file
    uploader = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=djm.SET_NULL,
        related_name='files')
    #: Users who authored the file
    authors = djm.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    #: Verbose authorship credit (for external authors)
    author_str = djm.CharField(max_length=256, null=True, blank=True)
    #: Digital object identifier
    doi = djm.URLField(null=True, blank=True)

    # Processed fields
    #: Timestamp of last analysis
    process_date = djm.DateTimeField(null=True, blank=True)
    #: The pages in text documents
    pages = ArrayField(djm.TextField(), null=True, blank=True)
    #: External links in this file
    links = ArrayField(djm.URLField(), null=True, blank=True)
    #: Parsing meta
    meta = djm.JSONField(null=True, blank=True)

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.hash})"
        return self.hash

    @property
    def can_preview(self):
        return self.mime in PREVIEWABLE_MIMES

    @property
    def hash_tag(self):
        return self.hash[:8]

    @property
    def size_str(self):
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1048576:
            return f"{int(self.size / 1024)} KB"
        else:
            return f"{int(self.size / 1048576)} MB"

    def get_absolute_url(self):
        return reverse('college:file', args=[self.hash])

    def get_download_url(self):
        return reverse('college:file_download', args=[self.hash])

    def analyse(self):
        if self.external:
            file_path = f"/{settings.EXTERNAL_ROOT}/{self.hash[:2]}/{self.hash[2:]}"
            try:
                data = files.parse(file_path, self.hash)
            except:
                print(f"File {file_path} failed to parse.")
                traceback.print_exc()
                return

            if data:
                # data.pop('images')
                self.links = data.pop('links')
                self.pages = data.pop('pages')
                self.meta = data
                self.process_date = timezone.now()
                try:
                    self.save()
                except Exception:
                    traceback.print_exc()
        else:
            raise NotImplementedError()


@reversion.register()
class ClassFile(Importable):
    """A file attachment which was shared to a class"""
    #: Class instance where this size is featured
    file = djm.ForeignKey(File, on_delete=djm.PROTECT, related_name='class_files')
    #: Class instance where this size is featured
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.PROTECT, related_name='files')
    #: File name
    name = djm.CharField(max_length=256)
    #: Type of file being shared
    category = djm.IntegerField(choices=ctypes.FileType.CHOICES)
    #: Availability of this file (who can see it)
    visibility = djm.IntegerField(choices=ctypes.FileVisibility.CHOICES, default=ctypes.FileVisibility.NOBODY)
    #: Whether this file is an official material to this class instance
    official = djm.BooleanField(default=False)
    #: Datetime at which this file got inserted in this class
    upload_datetime = djm.DateTimeField(auto_now_add=True)
    #: User who inserted the file in this class
    uploader = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=djm.SET_NULL,
        related_name='class_files')
    #: Uploader name fallback (due to imports who cannot be resolved to a user)
    uploader_teacher = djm.ForeignKey(
        Teacher,
        null=True,
        blank=True,
        on_delete=djm.SET_NULL,
        related_name='class_files')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('college:class_instance_file', args=[self.class_instance.id, self.id])

    def get_download_url(self):
        return reverse('college:class_instance_file_download', args=[self.class_instance.id, self.id])

    def short_name(self):
        if len(self.name) > 70:
            return self.name[:66] + '...'
        return self.name


class ClassInstanceAnnouncement(Importable):
    """Announcement which was broadcast to a class"""
    #: Class instance where the broadcast occurred
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.PROTECT, related_name='announcements')
    #: User who broadcasted the message
    user = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, on_delete=djm.PROTECT,
        related_name='class_announcements')
    #: Message title
    title = djm.CharField(max_length=256)
    #: Message content
    message = djm.TextField()
    #: Datetime of the announcement
    datetime = djm.DateTimeField()


# Course curriculum related classes

class CurricularComponent(PolymorphicModel):
    """ A component in the construction of a curricular plan. """
    #: Verbose name that identifies this component
    text_id = djm.CharField(null=True, blank=True, max_length=100, db_index=True, unique=True)
    #: The minimum year a student must be on to be allowed to have this component
    min_year = djm.IntegerField(default=0)
    #: The period of min_year a student must be on to be allowed to have this component
    min_period = djm.IntegerField(null=True, blank=True, choices=ctypes.Period.CHOICES, default=None)
    #: The year on which this class is suggested to happen
    suggested_year = djm.IntegerField(null=True, blank=True)
    #: The period on which this class is suggested to happen
    suggested_period = djm.IntegerField(null=True, blank=True, choices=ctypes.Period.CHOICES)
    #: Whether this component is required
    required = djm.BooleanField(default=True)
    #: Cached field, the aggregation of curricular plan until this component
    aggregation = djm.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ['suggested_year', 'suggested_period']

    def __str__(self):
        return f'{self.text_id}'

    def update_aggregation(self):
        raise NotImplementedError()

    def get_leaves(self):
        raise NotImplementedError()

    def update_leaves(self):
        """ Can be used to fix broken aggregation chains """
        [leaf.update_aggregation() for leaf in self.get_leaves()]

    @property
    def short_min_period(self):
        return ctypes.Period.SHORT_CHOICES[self.min_period - 1]

    @property
    def short_suggested_period(self):
        return ctypes.Period.SHORT_CHOICES[self.suggested_period - 1]


class CurricularClassComponent(CurricularComponent):
    """ A class in a curricular plan. """
    #: The class this component refers to
    klass = djm.ForeignKey(Class, on_delete=djm.PROTECT, related_name='curricular_components')

    def __str__(self):
        return f'{self.klass.name} ({self.klass.iid};{self.text_id})'

    def save(self, *args, **kwargs):
        super(CurricularClassComponent, self).save(*args, **kwargs)
        if kwargs.get('update_fields') != ['aggregation']:
            self.update_aggregation()

    def calc_aggregation(self):
        return {
            'id': self.id,
            'type': 'class',
            'class': self.klass_id,
            'filtered': False,
        }

    def update_aggregation(self):
        aggregation = self.calc_aggregation()
        if self.aggregation != aggregation:
            self.aggregation = aggregation
            self.save(update_fields=['aggregation'])
        for parent in self.parents.all():
            parent.update_aggregation()

    def get_leaves(self):
        return [self]


class AbstractCurricularBlockComponent(djm.Model):
    """ Generic fields that block-alike components. """
    #: A verbal name for this block
    name = djm.CharField(max_length=100)
    #: The minimum number of subcomponents of this block that must be completed
    min_components = djm.IntegerField(default=0)
    #: The minimum number of credits that a student must obtain from this block
    min_credits = djm.IntegerField(default=0)
    #: The amount of credits one is suggested to perform in this component during this occasion
    suggested_credits = djm.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    def _partial_aggregation(self):
        return {
            'name': self.name,
            'min_components': self.min_components,
            'min_credits': self.min_credits,
            'suggested_credits': self.suggested_credits,
            'filtered': False
        }


class CurricularBlockComponent(AbstractCurricularBlockComponent, CurricularComponent):
    """ A group of class components. """
    #: Subcomponents that are a part of this block
    children = djm.ManyToManyField(CurricularComponent, related_name='parents')

    def __str__(self):
        return f'{self.name} ({self.text_id})'

    def save(self, *args, **kwargs):
        super(CurricularBlockComponent, self).save(*args, **kwargs)
        if kwargs.get('update_fields') != ['aggregation']:
            self.update_aggregation()

    def calc_aggregation(self):
        # TODO get rid of filter after the aggregation is automatically performed on creation
        children = list(filter(lambda c: len(c) > 0, map(lambda child: child.aggregation, self.children.all())))
        return {
            'id': self.id,
            'type': 'block',
            'children': children,
            **self._partial_aggregation()
        }

    def update_aggregation(self):
        aggregation = self.calc_aggregation()
        if self.aggregation != aggregation:
            self.aggregation = aggregation
            self.save(update_fields=['aggregation'])
        for parent in self.parents.all():
            parent.update_aggregation()
        [parent.update_aggregation() for parent in self.parents.all()]
        for variant in self.block_variants.all():
            variant.update_aggregation()
        for curriculums in self.curriculums.all():
            curriculums.update_aggregation()

    def get_leaves(self):
        return [leaf for child in self.children.all() for leaf in child.get_leaves()]


# # With relationship data separated from the entity
# class CurricularBlockSubcomponent(djm.Model):
#     parent = djm.ForeignKey(CurricularBlockComponent, on_delete=djm.PROTECT, related_name='children_rel')
#     child = djm.ForeignKey(CurricularComponent, on_delete=djm.CASCADE, related_name='parent_rel')
#     required = djm.BooleanField(default=True)
#     #: Cached field, the aggregation of curricular plan until this component
#     aggregation = djm.JSONField(blank=True, default=dict)
#
#     class Meta:
#         unique_together = [('parent', 'child')]


class CurricularBlockVariantComponent(AbstractCurricularBlockComponent, CurricularComponent):
    """ A variant of a class block, with additional restrictions. """
    #: Subcomponents that are to be ignored in the children
    blocked_components = djm.ManyToManyField(CurricularComponent, blank=True, related_name='curricular_blocks')
    #: The subcomponent this variant overrides
    block = djm.ForeignKey(CurricularBlockComponent, on_delete=djm.PROTECT, related_name='block_variants')

    def __str__(self):
        return f'{self.name} ({self.text_id})'

    def save(self, *args, **kwargs):
        super(CurricularBlockVariantComponent, self).save(*args, **kwargs)
        if kwargs.get('update_fields') != ['aggregation']:
            self.update_aggregation()

    def calc_aggregation(self):
        block_aggregation = self.block.aggregation
        blocked_component_ids = self.blocked_components.values_list('id', flat=True)
        CurricularBlockVariantComponent.__aggregation_filter(block_aggregation, blocked_component_ids)
        return {
            'id': self.id,
            'type': 'block_variant',
            'block': block_aggregation,
            **self._partial_aggregation(),
        }

    def update_aggregation(self):
        aggregation = self.calc_aggregation()
        if self.aggregation != aggregation:
            self.aggregation = aggregation
            self.save(update_fields=['aggregation'])
        for parent in self.parents.all():
            parent.update_aggregation()

    def get_leaves(self):
        return self.block.get_leaves()

    @staticmethod
    def __aggregation_filter(node, component_ids):
        """
        Filters components from a component node
        :param node: component node being filtered
        :param component_ids: undesired ids
        """
        for child in node['children']:
            if child['id'] in component_ids:
                child['filtered']: True

            if (ctype := child['type']) == 'block_variant':
                CurricularBlockVariantComponent.__aggregation_filter(child['block'], component_ids)
            elif ctype == 'block':
                CurricularBlockVariantComponent.__aggregation_filter(child, component_ids)


class Curriculum(djm.Model):
    """
    The declaration of classes that make a course structure.
    Ideally this is a tree that connects to nodes shared among courses and applies filters to them.
    """
    #: The course tho which this curriculum belongs
    course = djm.ForeignKey(Course, on_delete=djm.CASCADE, related_name='curriculums')
    #: The year on which this curricular plan started to apply
    from_year = djm.IntegerField(null=True, blank=True)
    #: The year on which this curricular plan stopped applying
    to_year = djm.IntegerField(null=True, blank=True)
    #: The root block that describes the course curriculum
    root = djm.ForeignKey(CurricularBlockComponent, on_delete=djm.PROTECT, related_name='curriculums')
    #: Cached field, the aggregation of the simplified curricular plan
    aggregation = djm.JSONField(default=dict)

    def __str__(self):
        return f'{self.course} ({self.from_year} - {self.to_year})'

    @property
    def simple_aggregation(self):
        return self.aggregation.get('children')

    def calc_aggregation(self):
        aggregation = self.root.aggregation
        while Curriculum.__clean_aggregation(aggregation):
            pass  # Reapply function while there are changes being made
        id_set = set()
        class_set = set()
        Curriculum.__collect_ids(aggregation, id_set, class_set)
        aggregation['_ids'] = list(id_set)
        aggregation['_classes'] = list(class_set)
        return aggregation

    def update_aggregation(self):
        aggregation = self.calc_aggregation()
        if self.aggregation != aggregation:
            self.aggregation = aggregation
            self.save(update_fields=['aggregation'])

    def update_leaves(self):
        [leaf.update_aggregation() for leaf in self.root.get_leaves()]

    @staticmethod
    def __clean_aggregation(root):
        if (rtype := root['type']) == 'block_variant':
            if (child_block := root['block'])['filtered']:
                root.pop('block')
                root['filtered'] = True
                return 1
            else:
                changes = Curriculum.__clean_aggregation(child_block)
                root['id'] = child_block['id']
                root['children'] = child_block['children']
                root['type'] = 'block'
                for attr in ('name', 'min_components', 'min_credits', 'min_components', 'suggested_credits'):
                    if not root[attr]:
                        root[attr] = child_block[attr]
                root.pop('block')
                return changes + 1
        elif rtype == 'block':
            removed_count = 0
            for child in root['children']:
                if child['filtered']:
                    removed_count += 1
                    root['children'].remove(child)
                else:
                    removed_count += Curriculum.__clean_aggregation(child)
            if len(root['children']) == 0:
                root['filtered'] = True
            return removed_count
        return 0

    @staticmethod
    def __collect_ids(root, node_id_set, class_id_set):
        node_id_set.add(root['id'])
        if (rtype := root['type']) == 'block_variant':
            Curriculum.__collect_ids(root['block'], node_id_set, class_id_set)
        elif rtype == 'block':
            for child in root['children']:
                Curriculum.__collect_ids(child, node_id_set, class_id_set)
        elif rtype == 'class':
            class_id_set.add(root['class'])
