from django.db import models
from django.db.models import Model, IntegerField, TextField, ForeignKey, ManyToManyField, BooleanField, DateField, \
    DateTimeField, NullBooleanField

from college import choice_types as ctypes

CLIPY_TABLE_PREFIX = 'clip_'


class TemporalEntity:
    """
    | An abstract entity which has a timespan (in years).
    | This timespan can lack a start, end or both since its based on crawled information.
    """
    first_year = IntegerField(blank=True, null=True)  #: The first year of the timespan (inclusive)
    last_year = IntegerField(blank=True, null=True)  #: The last year of the timespan (inclusive)

    def has_time_range(self):
        """
        Checks if the time has been set
        :return:
        """
        return not (self.first_year is None or self.last_year is None)


class Institution(TemporalEntity, Model):
    """
    | Once upon a time CLIP had several institutions under the same system.
    | Although that is no longer the case, the data is still there.
    """
    id = IntegerField(primary_key=True)  #: CLIP internal code for this institution
    abbreviation = TextField(max_length=10)  #: The institution string abbreviation
    name = TextField(null=True, max_length=50)  #: The institution name

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'institutions'

    def __str__(self):
        return self.abbreviation


class Building(Model):
    """
    A :py:class:`Classroom` location. This is not guaranteed to be an actual building. Why? Because CLIP!
    """
    id = IntegerField(primary_key=True)
    name = TextField(max_length=30)  #: The CLIP internal building string representation
    institution = ForeignKey(Institution, on_delete=models.PROTECT, db_column='institution_id',
                             related_name='buildings')  #: CLIP institution relation

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'buildings'

    def __str__(self):
        return self.name


class Department(Model, TemporalEntity):
    """
    | A department is an entity responsible for teaching several :py:class:`Class` es.
    | It also creates courses, although a course doesn't exclusively rely on its main department.
    """
    id = IntegerField(primary_key=True)  #: CLIP internal code for this department
    name = TextField(max_length=50)  #: Department name
    institution = ForeignKey(Institution, on_delete=models.PROTECT, db_column='institution_id',
                             related_name='departments')  #: CLIP institution relation

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'departments'

    def __str__(self):
        return "{}({})".format(self.name, self.id)


class Class(Model):
    """
    | A class is an abstract idea of a subject.
    | It is a timeless concept, refer to :py:class:`ClassInstance` for the temporal version.
    """
    id = IntegerField(primary_key=True)
    iid = IntegerField()  #: CLIP class internal code
    name = TextField()
    abbreviation = TextField()  #: CLIP string abbreviation of this class name
    ects = IntegerField(null=True)  #: ECTS are stored as halves. 2 DB ECTS = 1 real ECTS
    department = ForeignKey(Department, on_delete=models.PROTECT, db_column='department_id', related_name='classes')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'classes'

    def __str__(self):
        return "{}({})".format(self.name, self.iid)


class Room(Model):
    """
    The CLIP notion of a classroom is either a generic room, laboratory, auditorium or even a random place.
    """
    id = IntegerField(primary_key=True)
    name = TextField(max_length=70)  #: CLIP string representation of the classroom name
    room_type = IntegerField()  # TODO choices
    building = ForeignKey(Building, on_delete=models.PROTECT, db_column='building_id', related_name='classrooms')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'rooms'

    def __str__(self):
        return "{} - {}".format(self.name, self.building.name)


class Teacher(Model, TemporalEntity):
    """
    | A person who teaches.
    | Note that there is an intersection between students and teachers. A student might become a teacher.
    """
    id = IntegerField(primary_key=True)
    iid = IntegerField()
    name = TextField(max_length=100)  #: Teacher name, which is what distinguishes them right now.
    department = ForeignKey(Department, on_delete=models.PROTECT, db_column='department_id', related_name='teachers')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'teachers'

    def __str__(self):
        return self.name


class ClassInstance(Model):
    """
    The temporal instance of a :py:class:`Class`.
    """
    id = IntegerField(primary_key=True)
    parent = ForeignKey(Class, on_delete=models.PROTECT, db_column='class_id', related_name='instances')
    period = IntegerField(db_column='period_id', choices=ctypes.Period.CHOICES)
    year = IntegerField()
    description_pt = TextField(null=True)
    description_en = TextField(null=True)
    description_edited_datetime = DateTimeField(null=True)
    description_editor = TextField(null=True)
    objectives_pt = TextField(null=True)
    objectives_en = TextField(null=True)
    objectives_edited_datetime = DateTimeField(null=True)
    objectives_editor = TextField(null=True)
    requirements_pt = TextField(null=True)
    requirements_en = TextField(null=True)
    requirements_edited_datetime = DateTimeField(null=True)
    requirements_editor = TextField(null=True)
    competences_pt = TextField(null=True)
    competences_en = TextField(null=True)
    competences_edited_datetime = DateTimeField(null=True)
    competences_editor = TextField(null=True)
    program_pt = TextField(null=True)
    program_en = TextField(null=True)
    program_edited_datetime = DateTimeField(null=True)
    program_editor = TextField(null=True)
    bibliography_pt = TextField(null=True)
    bibliography_en = TextField(null=True)
    bibliography_edited_datetime = DateTimeField(null=True)
    bibliography_editor = TextField(null=True)
    assistance_pt = TextField(null=True)
    assistance_en = TextField(null=True)
    assistance_edited_datetime = DateTimeField(null=True)
    assistance_editor = TextField(null=True)
    teaching_methods_pt = TextField(null=True)
    teaching_methods_en = TextField(null=True)
    teaching_methods_edited_datetime = DateTimeField(null=True)
    teaching_methods_editor = TextField(null=True)
    evaluation_methods_pt = TextField(null=True)
    evaluation_methods_en = TextField(null=True)
    evaluation_methods_edited_datetime = DateTimeField(null=True)
    evaluation_methods_editor = TextField(null=True)
    extra_info_pt = TextField(null=True)
    extra_info_en = TextField(null=True)
    extra_info_edited_datetime = DateTimeField(null=True)
    extra_info_editor = TextField(null=True)
    working_hours = TextField(null=True)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'class_instances'

    def __str__(self):
        return "{} ({} of {})".format(self.parent, self.period, self.year)


class Course(TemporalEntity, Model):
    """
    Courses define their :py:class:`Student` s academic routes.
    """
    id = IntegerField(primary_key=True)
    iid = IntegerField()
    name = TextField(max_length=70)
    abbreviation = TextField(null=True, max_length=15)
    institution = ForeignKey(Institution, on_delete=models.PROTECT, db_column='institution_id', related_name='courses')
    degree = IntegerField(db_column='degree_id', null=True, blank=True, choices=ctypes.Degree.CHOICES)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'courses'

    def __str__(self):
        return "{}(ID:{} Abbreviation:{}, Degree:{})".format(self.name, self.iid, self.abbreviation, self.degree)


class Student(Model, TemporalEntity):
    """
    | A student can be one of many "aliases" a person can have.
    | Every student has a person behind, but a person can be several students.
    | If a person transfers from one :py:class:`Course` to another, becomes a different student.
    | Why? Because that's how CLIP works!
    """
    id = IntegerField(primary_key=True)
    name = IntegerField()
    iid = IntegerField()
    """ 
    CLIP public representation of a student id (eg: 12345).
    "internal" is misleading since there's a private one which seems not to be crawlable
    at least not without administrative privileges.
    """
    abbreviation = TextField(null=True, max_length=30)
    course = ForeignKey(Course, on_delete=models.PROTECT, db_column='course_id', related_name='students')
    #: The course a student is known to be enrolled to. FIXME couldn't this be null?
    institution = ForeignKey(Institution, on_delete=models.PROTECT, db_column='institution_id', related_name='students')
    gender = NullBooleanField(null=True)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'students'

    def __str__(self):
        return "{}, {}".format(self.name, self.iid, self.abbreviation)


class Admission(Model):
    """
    | Every year there's a national contest for college admission.
    | This entity stores that contest's results as well as the last known student state
    | (eg. If a student gives up after 10 years, the state will say it)
    """
    id = IntegerField(primary_key=True)
    student = ForeignKey(Student, on_delete=models.PROTECT, db_column='student_id', related_name='admissions')
    course = ForeignKey(Course, on_delete=models.PROTECT, db_column='course_id', related_name='admissions')
    phase = IntegerField(null=True)
    year = IntegerField(null=True)
    option = IntegerField(null=True)
    #: This is not studied enough, but basically it's a text representation of the student whereabouts as of check_date
    state = TextField(null=True, max_length=50)
    #: The date on which this admission was checked. Relevant because of the state field.
    check_date = DateTimeField()
    name = TextField(null=True, max_length=100)
    """ 
    | Student full name. This is ``null`` if there's a matching :py:class:`Student`.
    | The student field has to be set if this is ``null``.
    """

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'admissions'

    def __str__(self):
        return ("{}, admitted to {}({}) (option {}) at the phase {} of the {} contest. {} as of {}".format(
            (self.student.name if self.student_id is not None else self.name),
            self.course.abbreviation, self.course_id, self.option, self.phase, self.year, self.state,
            self.check_date))


class Enrollment(Model):
    """
    | Representation of a :py:class:`Student` relation to a :py:class:`ClassInstance`.
    """
    id = IntegerField(primary_key=True)
    student = ForeignKey(Student, on_delete=models.PROTECT, db_column='student_id', related_name='enrollments')
    class_instance = ForeignKey(
        ClassInstance, on_delete=models.PROTECT, db_column='class_instance_id', related_name='enrollments')
    attempt = IntegerField(null=True)
    student_year = IntegerField(null=True)
    statutes = TextField(blank=True, null=True, max_length=20)
    observation = TextField(blank=True, null=True, max_length=30)
    attendance = NullBooleanField(null=True)
    attendance_date = DateField()
    improved = BooleanField()
    improvement_grade = IntegerField()
    improvement_grade_date = DateField(null=True)
    continuous_grade = IntegerField()
    continuous_grade_date = DateField(null=True)
    exam_grade = IntegerField()
    exam_grade_date = DateField()
    special_grade = IntegerField()
    special_grade_date = DateField(null=True)
    approved = NullBooleanField(null=True)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'enrollments'

    def __str__(self):
        return "{} enrolled to {}, attempt:{}, student year:{}, statutes:{}, obs:{}".format(
            self.student, self.class_instance, self.attempt, self.student_year, self.statutes, self.observation)


class Turn(Model):
    """
    | Turns are a timeless and spaceless concept, they belong to a :py:class:`ClassInstance` and have
    | :py:class:`TurnInstance` s.
    | :py:class:`Student` s are connected to turn's instead of instances.
    | One cannot belong to an instance of a turn and not to the others.
    """
    id = IntegerField(primary_key=True)
    number = IntegerField()
    type = IntegerField(choices=ctypes.TurnType.CHOICES, db_column='type_id')
    class_instance = ForeignKey(
        ClassInstance, on_delete=models.PROTECT, db_column='class_instance_id', related_name='turns')
    minutes = IntegerField(null=True)
    enrolled = IntegerField(null=True)
    capacity = IntegerField(null=True)
    routes = TextField(blank=True, null=True, max_length=30)
    restrictions = TextField(blank=True, null=True, max_length=30)
    state = TextField(blank=True, null=True, max_length=30)
    students = ManyToManyField(Student, through='TurnStudent', related_name='turns')
    teachers = ManyToManyField(Teacher, through='TurnTeacher', related_name='turns')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turns'

    def __str__(self):
        return "{}{} of {}".format(ctypes.TurnType.CHOICES[self.type], self.number, self.class_instance)


class TurnInstance(Model):
    """
    Turns instances position a :py:class:`Turn` in time and space.
    """
    id = IntegerField(primary_key=True)
    turn = ForeignKey(Turn, on_delete=models.PROTECT, db_column='turn_id', related_name='instances')
    start = IntegerField()  #: Turn start day minute (0 is midnight, 120 is 2:00)
    end = IntegerField(null=True)  #: Turn end day minute (0 is midnight, 120 is 2:00)
    weekday = IntegerField(null=True)  #: Weekday, starting on monday=0
    classroom = ForeignKey(Room, on_delete=models.PROTECT, db_column='classroom_id', related_name='turn_instances')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_instances'


class TurnTeacher(Model):
    """
     :py:class:`Teacher` to :py:class:`Turn` relationship.
    """
    turn = ForeignKey(Turn, on_delete=models.PROTECT)
    teacher = ForeignKey(Teacher, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_students'


class TurnStudent(Model):
    """
     :py:class:`Student` to :py:class:`Turn` relationship.
    """
    turn = ForeignKey(Turn, on_delete=models.PROTECT, db_column='turn_id')
    student = ForeignKey(Student, on_delete=models.PROTECT, db_column='student_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_students'
