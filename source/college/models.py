import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models as djm
from django.contrib.gis.db import models as gis
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, F
from django.urls import reverse
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from users.models import Activity
from feedback import models as feedback
from settings import COLLEGE_YEAR, COLLEGE_PERIOD
from . import choice_types as ctypes

logger = logging.getLogger(__name__)


class Importable(djm.Model):
    """Objects which were imported from other supernova-alike systems trough some driver."""
    #: The ID for this object in an external system (its primary key)
    external_id = djm.IntegerField(null=True, blank=True, unique=True)
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


class Student(Importable):
    """
    | A student instance.
    | Each user can have multiple instances if the user enrolled multiple times to multiple courses.
    """
    #: Full teacher name (eventually redundant, useful for registrations)
    name = djm.TextField(max_length=200, null=True)
    #: User this student is associated with
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=djm.CASCADE, related_name='students')
    #: The public number which identifies this student
    number = djm.IntegerField(null=True, blank=True, unique=True)
    #: The public textual abbreviation which identifies this student
    abbreviation = djm.CharField(null=True, blank=True, max_length=64)
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


class Building(Importable):
    """A physical building withing the campus"""
    #: Full name
    name = djm.CharField(max_length=32, unique=True)
    #: Abbreviated name
    abbreviation = djm.CharField(max_length=16, unique=True, null=True)
    #: Tag in the campus map
    map_tag = djm.CharField(max_length=20, unique=True)
    #: Geographical center
    location = gis.PointField(geography=True, null=True)
    #:  Picture illustrating this building
    picture = djm.ImageField(upload_to=building_pic_path, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


def department_pic_path(department, filename):
    return f'c/d/{department.id}/pic.{filename.split(".")[-1].lower()}'


class Department(Importable):
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
    #: Changes performed on this department object
    changes = GenericRelation('AcademicDataChange', related_query_name='department')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


def place_pic_path(room, filename):
    return f'c/b/{room.id}/pic.{filename.split(".")[-1].lower()}'


class Place(djm.Model):
    """A generic geographical place"""
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
    description = djm.TextField(max_length=2048, null=True, blank=True)
    #: Verbose description of equipment in this room
    equipment = djm.TextField(max_length=2048, null=True, blank=True)
    #: Whether the room still exists as referred to by this object
    extinguished = djm.BooleanField(default=False)

    class Meta:
        ordering = ('floor', 'door_number', 'name')
        # unique_together = ('name', 'building', 'type') inheritance forbids this

    def __str__(self):
        return f'{self.building.abbreviation} {self.name}'

    def long__str(self):
        return f'{self.building}, {ctypes.RoomType.CHOICES[self.type - 1][1]} {self.name}'

    def schedule_str(self):
        return f'Ed {self.building.abbreviation}, {ctypes.RoomType.CHOICES[self.type - 1][1]} {self.name}'


class Course(Importable):
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
    #: Teacher which coordinates this course
    coordinator = djm.ForeignKey(
        'Teacher',
        null=True,
        blank=True,
        on_delete=djm.PROTECT,
        related_name='coordinated_courses')
    #: URL to this course's official page
    url = djm.URLField(max_length=256, null=True, blank=True)
    #: Changes performed on this course object
    changes = GenericRelation('AcademicDataChange', related_query_name='course')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{ctypes.Degree.name(self.degree)} em {self.name}'

    @property
    def description_html(self):
        return markdownify(self.description)


class Class(Importable):
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
    #: URL to this classe's official page
    url = djm.URLField(max_length=256, null=True, blank=True)
    #: Changes performed on this class object
    changes = GenericRelation('AcademicDataChange', related_query_name='klass')
    # Cached
    #: The average grade in this instance
    avg_grade = djm.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'classes'

    def __str__(self):
        return self.name

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


class ClassInstance(Importable):
    """An instance of a class with an associated point in time"""
    #: Class this refers to
    parent = djm.ForeignKey(Class, on_delete=djm.PROTECT, related_name='instances')
    #: Department this instance belonged to
    department = djm.ForeignKey(Department, on_delete=djm.PROTECT, related_name='class_instances')
    #: Period this happened on (enumeration)
    period = djm.IntegerField(choices=ctypes.Period.CHOICES)
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
    #: Changes performed on this class instance object
    changes = GenericRelation('AcademicDataChange', related_query_name='class_instance')
    # Cached
    #: The average grade in this instance
    avg_grade = djm.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ['parent', 'period', 'year']

    def __str__(self):
        return f"{self.parent.abbreviation}, {self.get_period_display()} de {self.year}"

    @property
    def full_str(self):
        return f"{self.parent.name}, {self.get_period_display()} de {self.year}"

    @property
    def occasion(self):
        return f'{self.get_period_display()}, {self.year - 1}/{self.year}'

    @property
    def short_occasion(self):
        return f'{ctypes.Period.SHORT_CHOICES[self.period - 1]} {self.year - 2001}/{self.year - 2000}'

    def get_absolute_url(self):
        return reverse('college:class_instance', args=[self.id])


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
        return f'{self.info} {self.time}- {self.class_instance}'

    @property
    def to_time(self):
        delta = timedelta(minutes=self.duration)
        return (datetime.combine(datetime.today(), self.time) + delta).time()


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

    def intersects(self, shift_instance):
        # Same weekday AND A starts before B ends and B starts before A ends
        return self.weekday == shift_instance.weekday and \
               self.start < shift_instance.start + shift_instance.duration and \
               shift_instance.start < self.start + self.duration

    def weekday_pt(self):
        return ctypes.WEEKDAY_CHOICES[self.weekday][1]

    def start_str(self):
        return self.minutes_to_str(self.start)

    def end_str(self):
        return self.minutes_to_str(self.start + self.duration)

    def happening(self):
        now = datetime.now()
        if not (self.shift.class_instance.year == COLLEGE_YEAR and self.shift.class_instance.period == COLLEGE_PERIOD):
            return False

        # same weekday and within current time interval
        return self.weekday == now.isoweekday() and self.start < now.hour * 60 + now.min < self.start + self.duration

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


class Teacher(Importable):
    """
    | A person who teaches or investigates.
    | Note that there is an intersection between students and teachers. A student might become a teacher.
    """
    #: Full teacher name (eventually redundant, useful for registrations)
    name = djm.TextField(max_length=200)
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
    abbreviation = djm.CharField(null=True, blank=True, max_length=64)
    #: URL to this teacher's official page
    url = djm.URLField(max_length=256, null=True, blank=True)
    #: This teacher's email
    email = djm.EmailField(max_length=256, null=True, blank=True)
    #: Phone number in the format +country number,extension
    phone = djm.CharField(max_length=20, null=True, blank=True)
    #:  A picture of this teacher
    picture = djm.ImageField(upload_to=teacher_pic_path, null=True, blank=True)
    #:  The room that a teacher occupies
    room = djm.ForeignKey(Room, null=True, on_delete=djm.PROTECT, related_name='teachers')
    #: Changes performed on this teacher's object
    changes = GenericRelation('AcademicDataChange', related_query_name='teacher')
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


def file_upload_path(file, _):
    return f'file/{file.hash}'


PREVIEWABLE_MIMES = {
    'application/pdf',
}


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
    #: Changes performed on this file object
    changes = GenericRelation('AcademicDataChange', related_query_name='file')

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

    def get_absolute_url(self):
        return reverse('college:file', args=[self.hash])


class ClassFile(Importable):
    """A file attachment which was shared to a class"""
    #: Class instance where this size is featured
    file = djm.ForeignKey(File, on_delete=djm.PROTECT, related_name='class_files')
    #: Class instance where this size is featured
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.PROTECT, related_name='files')
    #: File name
    name = djm.CharField(null=True, blank=True, max_length=256)
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
    #: Changes performed on this class file object
    changes = GenericRelation('AcademicDataChange', related_query_name='class_file')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('college:class_instance_file', args=[self.class_instance.id, self.id])

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


class Curriculum(djm.Model):
    # TODO redo this. Ain't going to work like this.
    course = djm.ForeignKey(Course, on_delete=djm.CASCADE)
    corresponding_class = djm.ForeignKey(Class, on_delete=djm.PROTECT)  # Guess I can't simply call it 'class'
    period_type = djm.CharField(max_length=1, null=True, blank=True)  # 's' => semester, 't' => trimester, 'a' => anual
    period = djm.IntegerField(null=True, blank=True)
    year = djm.IntegerField()
    required = djm.BooleanField()

    class Meta:
        ordering = ['year', 'period_type', 'period']
        unique_together = ['course', 'corresponding_class']


class AcademicDataChange(Activity):
    """An activity is an action taken by a user at a given point in time."""
    content_type = djm.ForeignKey(ContentType, on_delete=djm.CASCADE)
    object_id = djm.PositiveIntegerField()
    changed_object = GenericForeignKey('content_type', 'object_id')
    #: A dict describing changes {attrs=>[], new=>{attr=>val}, old=>{attr=>val}}
    changes = djm.JSONField()

    class Meta:
        verbose_name_plural = "activities"

    def __str__(self):
        return f'Atributos {self.changes["attrs"]} alterados em {self.changed_object}.'
