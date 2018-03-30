from django.db import models
from django.db.models import Model, IntegerField, TextField, ForeignKey, ManyToManyField
from django.forms import DateTimeField

CLIPY_TABLE_PREFIX = 'clip_'


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


class Institution(TemporalEntity, Model):
    id = IntegerField(primary_key=True)
    internal_id = IntegerField()
    abbreviation = TextField(max_length=10)
    name = TextField(null=True, max_length=50)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'institutions'

    def __str__(self):
        return self.abbreviation


class Building(Model):
    id = IntegerField(primary_key=True)
    name = TextField(max_length=30)
    institution = ForeignKey(Institution, on_delete=models.PROTECT, db_column='institution_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'buildings'

    def __str__(self):
        return self.name


class Department(Model, TemporalEntity):
    id = IntegerField(primary_key=True)
    internal_id = TextField()
    name = TextField(max_length=50)
    institution = ForeignKey(Institution, on_delete=models.PROTECT, db_column='institution_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'departments'

    def __str__(self):
        return "{}({})".format(self.name, self.internal_id)


class Class(Model):
    id = IntegerField(primary_key=True)
    name = TextField(null=True)
    internal_id = TextField(null=True)
    department = ForeignKey(Department, on_delete=models.PROTECT, db_column='department_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'classes'

    def __str__(self):
        return "{}({})".format(self.name, self.internal_id)


class Classroom(Model):
    id = IntegerField(primary_key=True)
    name = TextField(max_length=70)
    building = ForeignKey(Building, on_delete=models.PROTECT, db_column='building_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'classrooms'

    def __str__(self):
        return "{} - {}".format(self.name, self.building.name)


class Teacher(Model):
    __tablename__ = CLIPY_TABLE_PREFIX + 'teachers'
    id = IntegerField(primary_key=True)
    name = TextField(max_length=100)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'teachers'

    def __str__(self):
        return self.name


class ClassInstance(Model):
    id = IntegerField(primary_key=True)
    parent = ForeignKey(Class, on_delete=models.PROTECT, db_column='class_id')
    period = ForeignKey(Period, on_delete=models.PROTECT, db_column='period_id', related_name='clip_class_instances')
    year = IntegerField()

    # regent = ForeignKey(ClipTeacher, on_delete=models.PROTECT, db_column='regent_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'class_instances'

    def __str__(self):
        return "{} ({} of {})".format(self.parent, self.period, self.year)


class Course(TemporalEntity, Model):
    id = IntegerField(primary_key=True)
    internal_id = IntegerField()
    name = TextField(max_length=70)
    abbreviation = TextField(null=True, max_length=15)
    institution = ForeignKey(Institution, on_delete=models.PROTECT, db_column='institution_id')
    degree = ForeignKey(Degree, on_delete=models.PROTECT, db_column='degree_id', null=True, blank=True,
                        related_name='clip_courses')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'courses'

    def __str__(self):
        return "{}(ID:{} Abbreviation:{}, Degree:{})".format(self.name, self.internal_id, self.abbreviation,
                                                             self.degree)


class Student(Model):
    id = IntegerField(primary_key=True)
    name = TextField()
    internal_id = IntegerField()
    abbreviation = TextField(null=True, max_length=30)
    course = ForeignKey(Course, on_delete=models.PROTECT, db_column='course_id')
    institution = ForeignKey(Institution, on_delete=models.PROTECT, db_column='institution_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'students'

    def __str__(self):
        return "{}, {}".format(self.name, self.internal_id, self.abbreviation)


class Admission(Model):
    id = IntegerField(primary_key=True)
    student = ForeignKey(Student, on_delete=models.PROTECT, db_column='student_id')
    course = ForeignKey(Course, on_delete=models.PROTECT, db_column='course_id')
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


class Enrollment(Model):
    id = IntegerField(primary_key=True)
    student = ForeignKey(Student, on_delete=models.PROTECT, db_column='student_id')
    class_instance = ForeignKey(ClassInstance, on_delete=models.PROTECT, db_column='class_instance_id')
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


class Turn(Model):
    id = IntegerField(primary_key=True)
    number = IntegerField()
    type = ForeignKey(TurnType, on_delete=models.PROTECT, related_name='clip_turns')
    class_instance = ForeignKey(ClassInstance, on_delete=models.PROTECT, db_column='class_instance_id')
    minutes = IntegerField(null=True)
    enrolled = IntegerField(null=True)
    capacity = IntegerField(null=True)
    routes = TextField(blank=True, null=True, max_length=30)
    restrictions = TextField(blank=True, null=True, max_length=30)
    state = TextField(blank=True, null=True, max_length=30)
    students = ManyToManyField(Student, through='TurnStudent')
    teachers = ManyToManyField(Teacher, through='TurnTeacher')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turns'

    def __str__(self):
        return "{}{} of {}".format(self.type.abbreviation.upper(), self.number, self.class_instance)


class TurnInstance(Model):
    id = IntegerField(primary_key=True)
    turn = ForeignKey(Turn, on_delete=models.PROTECT, db_column='turn_id')
    start = IntegerField()
    end = IntegerField(null=True)
    weekday = IntegerField(null=True)
    classroom = ForeignKey(Classroom, on_delete=models.PROTECT, db_column='classroom_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_instances'


class TurnTeacher(Model):
    turn = ForeignKey(Turn, on_delete=models.PROTECT)
    teacher = ForeignKey(Teacher, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_students'


class TurnStudent(Model):
    turn = ForeignKey(Turn, on_delete=models.PROTECT, db_column='turn_id')
    student = ForeignKey(Student, on_delete=models.PROTECT, db_column='student_id')

    class Meta:
        managed = False
        db_table = CLIPY_TABLE_PREFIX + 'turn_students'
