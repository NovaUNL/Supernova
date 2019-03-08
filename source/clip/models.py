from django.db import models as djm

from college import choice_types as ctypes

CLIPY_TABLE_PREFIX = 'clip_'


class TemporalEntity:
    """
    | An abstract entity which has a timespan (in years).
    | This timespan can lack a start, end or both since its based on crawled information.
    """
    first_year = djm.IntegerField(blank=True, null=True)  #: The first year of the timespan (inclusive)
    last_year = djm.IntegerField(blank=True, null=True)  #: The last year of the timespan (inclusive)

    def has_time_range(self):
        """
        Checks if the time has been set
        :return:
        """
        return not (self.first_year is None or self.last_year is None)


class Institution(TemporalEntity, djm.Model):
    """
    | Once upon a time CLIP had several institutions under the same system.
    | Although that is no longer the case, the data is still there.
    """
    id = djm.IntegerField(primary_key=True)  #: CLIP internal code for this institution
    abbreviation = djm.TextField(max_length=10)  #: The institution string abbreviation
    name = djm.TextField(null=True, max_length=50)  #: The institution name

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'institutions'

    def __str__(self):
        return self.abbreviation


class Building(djm.Model):
    """
    A :py:class:`Classroom` location. This is not guaranteed to be an actual building. Why? Because CLIP!
    """
    id = djm.IntegerField(primary_key=True)
    name = djm.TextField(max_length=30)  #: The CLIP internal building string representation

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'buildings'

    def __str__(self):
        return self.name


class Department(djm.Model, TemporalEntity):
    """
    | A department is an entity responsible for teaching several :py:class:`Class` es.
    | It also creates courses, although a course doesn't exclusively rely on its main department.
    """
    id = djm.IntegerField(primary_key=True)  #: CLIP internal code for this department
    name = djm.TextField(max_length=50)  #: Department name
    institution = djm.ForeignKey(Institution,
                                 on_delete=djm.PROTECT,
                                 db_column='institution_id',
                                 related_name='departments')  #: CLIP institution relation

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'departments'

    def __str__(self):
        return "{}({})".format(self.name, self.id)


class Class(djm.Model):
    """
    | A class is an abstract idea of a subject.
    | It is a timeless concept, refer to :py:class:`ClassInstance` for the temporal version.
    """
    id = djm.IntegerField(primary_key=True)
    iid = djm.IntegerField()  #: CLIP class internal code
    name = djm.TextField()
    abbreviation = djm.TextField()  #: CLIP string abbreviation of this class name
    ects = djm.IntegerField(null=True)  #: ECTS are stored as halves. 2 DB ECTS = 1 real ECTS
    department = djm.ForeignKey(Department, on_delete=djm.PROTECT, db_column='department_id', related_name='classes')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'classes'

    def __str__(self):
        return "{}({})".format(self.name, self.iid)


class Room(djm.Model):
    """
    The CLIP notion of a classroom is either a generic room, laboratory, auditorium or even a random place.
    """
    id = djm.IntegerField(primary_key=True)
    name = djm.TextField(max_length=70)  #: CLIP string representation of the classroom name
    room_type = djm.IntegerField(choices=ctypes.RoomType.CHOICES)
    building = djm.ForeignKey(Building, on_delete=djm.PROTECT, db_column='building_id', related_name='classrooms')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'rooms'

    def __str__(self):
        return "{} - {}".format(self.name, self.building.name)


class Teacher(djm.Model, TemporalEntity):
    """
    | A person who teaches.
    | Note that there is an intersection between students and teachers. A student might become a teacher.
    """
    id = djm.IntegerField(primary_key=True)
    iid = djm.IntegerField()
    name = djm.TextField(max_length=100)  #: Teacher name, which is what distinguishes them right now.
    department = djm.ForeignKey(Department, on_delete=djm.PROTECT, db_column='department_id', related_name='teachers')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'teachers'

    def __str__(self):
        return self.name


class ClassInstance(djm.Model):
    """
    The temporal instance of a :py:class:`Class`.
    """
    id = djm.IntegerField(primary_key=True)
    parent = djm.ForeignKey(Class, on_delete=djm.PROTECT, db_column='class_id', related_name='instances')
    period = djm.IntegerField(db_column='period_id', choices=ctypes.Period.CHOICES)
    year = djm.IntegerField()
    description_pt = djm.TextField(null=True)
    description_en = djm.TextField(null=True)
    description_edited_datetime = djm.DateTimeField(null=True)
    description_editor = djm.TextField(null=True)
    objectives_pt = djm.TextField(null=True)
    objectives_en = djm.TextField(null=True)
    objectives_edited_datetime = djm.DateTimeField(null=True)
    objectives_editor = djm.TextField(null=True)
    requirements_pt = djm.TextField(null=True)
    requirements_en = djm.TextField(null=True)
    requirements_edited_datetime = djm.DateTimeField(null=True)
    requirements_editor = djm.TextField(null=True)
    competences_pt = djm.TextField(null=True)
    competences_en = djm.TextField(null=True)
    competences_edited_datetime = djm.DateTimeField(null=True)
    competences_editor = djm.TextField(null=True)
    program_pt = djm.TextField(null=True)
    program_en = djm.TextField(null=True)
    program_edited_datetime = djm.DateTimeField(null=True)
    program_editor = djm.TextField(null=True)
    bibliography_pt = djm.TextField(null=True)
    bibliography_en = djm.TextField(null=True)
    bibliography_edited_datetime = djm.DateTimeField(null=True)
    bibliography_editor = djm.TextField(null=True)
    assistance_pt = djm.TextField(null=True)
    assistance_en = djm.TextField(null=True)
    assistance_edited_datetime = djm.DateTimeField(null=True)
    assistance_editor = djm.TextField(null=True)
    teaching_methods_pt = djm.TextField(null=True)
    teaching_methods_en = djm.TextField(null=True)
    teaching_methods_edited_datetime = djm.DateTimeField(null=True)
    teaching_methods_editor = djm.TextField(null=True)
    evaluation_methods_pt = djm.TextField(null=True)
    evaluation_methods_en = djm.TextField(null=True)
    evaluation_methods_edited_datetime = djm.DateTimeField(null=True)
    evaluation_methods_editor = djm.TextField(null=True)
    extra_info_pt = djm.TextField(null=True)
    extra_info_en = djm.TextField(null=True)
    extra_info_edited_datetime = djm.DateTimeField(null=True)
    extra_info_editor = djm.TextField(null=True)
    working_hours = djm.TextField(null=True)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'class_instances'

    def __str__(self):
        return "{} ({} of {})".format(self.parent, self.period, self.year)


class Course(TemporalEntity, djm.Model):
    """
    Courses define their :py:class:`Student` s academic routes.
    """
    id = djm.IntegerField(primary_key=True)
    iid = djm.IntegerField()
    name = djm.TextField(max_length=70)
    abbreviation = djm.TextField(null=True, max_length=15)
    institution = djm.ForeignKey(Institution, on_delete=djm.PROTECT, db_column='institution_id', related_name='courses')
    degree = djm.IntegerField(db_column='degree_id', null=True, blank=True, choices=ctypes.Degree.CHOICES)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'courses'

    def __str__(self):
        return "{}(ID:{} Abbreviation:{}, Degree:{})".format(self.name, self.iid, self.abbreviation, self.degree)


class Student(djm.Model, TemporalEntity):
    """
    | A student can be one of many "aliases" a person can have.
    | Every student has a person behind, but a person can be several students.
    | If a person transfers from one :py:class:`Course` to another, becomes a different student.
    | Why? Because that's how CLIP works!
    """
    id = djm.IntegerField(primary_key=True)
    name = djm.IntegerField()
    #: CLIP public representation of a student id (eg: 12345).
    iid = djm.IntegerField()
    abbreviation = djm.TextField(null=True, max_length=30)
    #: The course a student is known to be enrolled to. FIXME couldn't this be null?
    institution = djm.ForeignKey(Institution, on_delete=djm.PROTECT, db_column='institution_id',
                                 related_name='students')
    gender = djm.NullBooleanField(null=True)
    graduation_grade = djm.IntegerField(null=True)
    courses = djm.ManyToManyField(Course, through='StudentCourse', related_name='students')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'students'

    def __str__(self):
        return "{}, {}".format(self.name, self.iid, self.abbreviation)


class StudentCourse(djm.Model):
    id = djm.IntegerField(primary_key=True)
    course = djm.ForeignKey(Course, on_delete=djm.PROTECT, db_column='course_id', related_name='student_relations')
    students = djm.ForeignKey(Student, on_delete=djm.PROTECT, db_column='student_id', related_name='course_relations')
    year = djm.IntegerField

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'student_courses'


class Admission(djm.Model):
    """
    | Every year there's a national contest for college admission.
    | This entity stores that contest's results as well as the last known student state
    | (eg. If a student gives up after 10 years, the state will say it)
    """
    id = djm.IntegerField(primary_key=True)
    student = djm.ForeignKey(Student, on_delete=djm.PROTECT, db_column='student_id', related_name='admissions')
    course = djm.ForeignKey(Course, on_delete=djm.PROTECT, db_column='course_id', related_name='admissions')
    phase = djm.IntegerField(null=True)
    year = djm.IntegerField(null=True)
    option = djm.IntegerField(null=True)
    #: This is not studied enough, but basically it's a text representation of the student whereabouts as of check_date
    state = djm.TextField(null=True, max_length=50)
    #: The date on which this admission was checked. Relevant because of the state field.
    check_date = djm.DateTimeField()
    name = djm.TextField(null=True, max_length=100)
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


class Enrollment(djm.Model):
    """
    | Representation of a :py:class:`Student` relation to a :py:class:`ClassInstance`.
    """
    id = djm.IntegerField(primary_key=True)
    student = djm.ForeignKey(Student, on_delete=djm.PROTECT, db_column='student_id', related_name='enrollments')
    class_instance = djm.ForeignKey(
        ClassInstance, on_delete=djm.PROTECT, db_column='class_instance_id', related_name='enrollments')
    attempt = djm.IntegerField(null=True)
    student_year = djm.IntegerField(null=True)
    statutes = djm.TextField(blank=True, null=True, max_length=20)
    observation = djm.TextField(blank=True, null=True, max_length=30)
    attendance = djm.NullBooleanField(null=True)
    attendance_date = djm.DateField()
    improved = djm.BooleanField()
    improvement_grade = djm.IntegerField()
    improvement_grade_date = djm.DateField(null=True)
    continuous_grade = djm.IntegerField()
    continuous_grade_date = djm.DateField(null=True)
    exam_grade = djm.IntegerField()
    exam_grade_date = djm.DateField()
    special_grade = djm.IntegerField()
    special_grade_date = djm.DateField(null=True)
    approved = djm.NullBooleanField(null=True)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'enrollments'

    def __str__(self):
        return "{} enrolled to {}, attempt:{}, student year:{}, statutes:{}, obs:{}".format(
            self.student, self.class_instance, self.attempt, self.student_year, self.statutes, self.observation)


class Turn(djm.Model):
    """
    | Turns are a timeless and spaceless concept, they belong to a :py:class:`ClassInstance` and have
    | :py:class:`TurnInstance` s.
    | :py:class:`Student` s are connected to turn's instead of instances.
    | One cannot belong to an instance of a turn and not to the others.
    """
    id = djm.IntegerField(primary_key=True)
    number = djm.IntegerField()
    type = djm.IntegerField(choices=ctypes.TurnType.CHOICES, db_column='type_id')
    class_instance = djm.ForeignKey(
        ClassInstance, on_delete=djm.PROTECT, db_column='class_instance_id', related_name='turns')
    minutes = djm.IntegerField(null=True)
    enrolled = djm.IntegerField(null=True)
    capacity = djm.IntegerField(null=True)
    routes = djm.TextField(blank=True, null=True, max_length=30)
    restrictions = djm.TextField(blank=True, null=True, max_length=30)
    state = djm.TextField(blank=True, null=True, max_length=30)
    students = djm.ManyToManyField(Student, through='TurnStudent', related_name='turns')
    teachers = djm.ManyToManyField(Teacher, through='TurnTeacher', related_name='turns')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turns'

    def __str__(self):
        return "{}{} of {}".format(ctypes.TurnType.CHOICES[self.type-1][1], self.number, self.class_instance)


class TurnInstance(djm.Model):
    """
    Turns instances position a :py:class:`Turn` in time and space.
    """
    id = djm.IntegerField(primary_key=True)
    turn = djm.ForeignKey(Turn, on_delete=djm.PROTECT, db_column='turn_id', related_name='instances')
    #: Turn start day minute (0 is midnight, 120 is 2:00)
    start = djm.IntegerField()
    #: Turn end day minute (0 is midnight, 120 is 2:00)
    end = djm.IntegerField(null=True)
    #: Weekday, starting on monday=0
    weekday = djm.IntegerField(null=True)
    room = djm.ForeignKey(Room, on_delete=djm.PROTECT, db_column='room_id', related_name='turn_instances')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_instances'


class TurnTeacher(djm.Model):
    """
     :py:class:`Teacher` to :py:class:`Turn` relationship.
    """
    turn = djm.ForeignKey(Turn, on_delete=djm.PROTECT)
    teacher = djm.ForeignKey(Teacher, on_delete=djm.PROTECT)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_students'


class TurnStudent(djm.Model):
    """
     :py:class:`Student` to :py:class:`Turn` relationship.
    """
    turn = djm.ForeignKey(Turn, on_delete=djm.PROTECT, db_column='turn_id')
    student = djm.ForeignKey(Student, on_delete=djm.PROTECT, db_column='student_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_students'


class File(djm.Model):
    id = djm.IntegerField(primary_key=True)
    name = djm.TextField(null=True)
    type = djm.IntegerField(db_column='file_type')  # TODO choices
    size = djm.IntegerField()
    hash = djm.CharField(max_length=40, null=True)
    location = djm.TextField(null=True)
    mime = djm.TextField(null=True)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'files'


class ClassInstanceFile(djm.Model):
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.PROTECT, db_column='class_instance_id')
    file = djm.ForeignKey(File, on_delete=djm.PROTECT, db_column='file_id')
    upload_datetime = djm.DateTimeField()
    uploader = djm.TextField(max_length=100)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'class_instance_files'


class ClassEvaluation(djm.Model):
    id = djm.IntegerField(primary_key=True)
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.PROTECT, db_column='class_instance_id')
    datetime = djm.DateTimeField()
    type = djm.IntegerField(db_column='evaluation_type')  # TODO choices

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'class_evaluations'


class ClassInstanceMessages(djm.Model):
    id = djm.IntegerField(primary_key=True)
    class_instance = djm.ForeignKey(ClassInstance, on_delete=djm.PROTECT, db_column='class_instance_id')
    teacher = djm.ForeignKey(Teacher, on_delete=djm.PROTECT, db_column='teacher_id')
    title = djm.TextField(max_length=200)
    message = djm.TextField()
    upload_datetime = djm.DateTimeField()
    uploader = djm.TextField(max_length=100)
    datetime = djm.DateTimeField()

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'class_instance_messages'
