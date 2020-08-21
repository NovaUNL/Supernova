from django.test import TestCase

from college import models as college
from college import choice_types as ctypes
from clip import synchronization as sync


class SyncTest(TestCase):
    def setUp(self):
        self.populate()

    def populate(self):
        self.department = college.Department.objects.create(name="Default", external_id=100)
        self.class_ = college.Class.objects.create(
            name="Fooism",
            abbreviation="F",
            department=self.department,
            external_id=100)
        self.class_instance = college.ClassInstance.objects.create(
            parent=self.class_,
            year=2020,
            period=2,
            external_id=100,
            information=dict())
        self.turn = college.Turn.objects.create(
            class_instance=self.class_instance,
            number=1,
            turn_type=1,
            external_id=100)
        self.turn_instance = college.TurnInstance.objects.create(
            turn=self.turn,
            weekday=2,
            start=600,
            external_id=100)
        self.teacher = college.Teacher.objects.create(name="Dr. Bar", external_id=100)
        self.student = college.Student.objects.create(external_id=100)
        self.enrollment = college.Enrollment.objects.create(
            student=self.student,
            class_instance=self.class_instance,
            external_id=100)
        college.TurnStudents.objects.create(student=self.student, turn=self.turn)

    def test_departments_sync(self):
        upstream = [
            {"id": 100, "institution": 97747, "name": "Default"},
            {"id": 101, "institution": 97747, "name": "New"},
            {"id": 102, "institution": 123, "name": "Forbidden"},
        ]
        sync._upstream_sync_departments(upstream, False)
        self.assertEquals(college.Department.objects.count(), 2)
        self.assertTrue(college.Department.objects.get(external_id=101).name, "New")

    def test_department_sync(self):
        upstream = {
            "classes": [100, 1001, 1002, 1004],  # Current/Unassigned/Assigned to other/Unknown
            "institution": 97747,
            "name": "Default",
            "teachers": [100]
        }
        a = college.Class.objects.create(name="Missing in department", external_id=1001)
        b = college.Class.objects.create(
            name="Owned by other department",
            department=college.Department.objects.create(name="Other department", external_id=1001),
            external_id=1002)
        c = college.Class.objects.create(name="Does not belong anymore", department=self.department, external_id=1003)

        sync._upstream_sync_department(upstream, self.department, False)
        a.refresh_from_db()
        b.refresh_from_db()
        c.refresh_from_db()

        self.assertEquals(a.department, self.department)
        self.assertEquals(b.department, self.department)
        self.assertNotEqual(c.department, self.department)

    def test_class_sync(self):
        # TODO external id starting to refer to a whole different object, violate key uniqueness
        upstream = {
            "abbr": "New",
            "dept": self.department.external_id,
            "ects": 12,
            "id": 201,
            "iid": 201,
            "instances": [100, 1000, 1001],
            "name": "New Class"
        }

        sync._upstream_sync_class(upstream, 201, self.department, False)

        new_class = college.Class.objects.get(external_id=201)

        self.assertEquals(new_class.name, "New Class")
        self.assertEquals(new_class.abbreviation, "New")
        self.assertEquals(new_class.credits, 12)
        self.assertEquals(new_class.department, self.department)

        moved = college.ClassInstance.objects.create(
            parent=self.class_,
            year=2020,
            period=3,
            external_id=1000,
            disappeared=True,
            information=dict())
        stays = college.ClassInstance.objects.create(
            parent=new_class,
            year=2020,
            period=2,
            external_id=1001,
            information=dict())
        deleted = college.ClassInstance.objects.create(
            parent=new_class,
            year=2020,
            period=3,
            external_id=1002,
            information=dict())

        sync._upstream_sync_class(upstream, 201, self.department, False)
        moved.refresh_from_db()
        stays.refresh_from_db()
        deleted.refresh_from_db()

        self.assertEquals(moved.parent, self.class_)
        self.assertEquals(stays.parent, new_class)
        self.assertEquals(deleted.parent, new_class)
        self.assertTrue(moved.disappeared)
        self.assertFalse(stays.disappeared)
        self.assertTrue(deleted.disappeared)

        other_dept = college.Department.objects.create(name="Default", external_id=1001)
        upstream = {
            "abbr": "Newr",
            "dept": other_dept.external_id,
            "ects": 15,
            "id": 201,
            "iid": 201,
            "instances": [100, 1000, 1002],
            "name": "Newer Class"
        }

        sync._upstream_sync_class(upstream, 201, self.department, False)
        new_class.refresh_from_db()
        stays.refresh_from_db()
        deleted.refresh_from_db()

        self.assertEquals(new_class.name, "Newer Class")
        self.assertEquals(new_class.abbreviation, "Newr")
        self.assertEquals(new_class.credits, 15)
        self.assertEquals(new_class.department, other_dept)
        self.assertEquals(stays.parent, new_class)
        self.assertEquals(deleted.parent, new_class)
        self.assertTrue(stays.disappeared)
        self.assertFalse(deleted.disappeared)

    def test_class_instance_sync(self):
        upstream = {
            "class_id": self.class_.external_id,
            "enrollments": [100, 1000, 1001],
            "evaluations": [],
            "id": 200,
            "info": {'foo': 'bar'},
            "period": 1,
            "turns": [100, 1000, 1001],
            "working_hours": 10,
            "year": 2020
        }
        sync._upstream_sync_class_instance(upstream, 200, self.class_, False)

        new_instance = college.ClassInstance.objects.get(external_id=200)

        self.assertEquals(new_instance.information, {'upstream': {'foo': 'bar'}})
        self.assertEquals(new_instance.period, upstream['period'])
        self.assertEquals(new_instance.year, upstream['year'])

        turn_moved = college.Turn.objects.create(
            class_instance=self.class_instance,
            number=4,
            turn_type=1,
            external_id=1000)
        turn_stays = college.Turn.objects.create(
            class_instance=new_instance,
            number=2,
            turn_type=1,
            external_id=1001)
        turn_deleted = college.Turn.objects.create(
            class_instance=new_instance,
            number=3,
            turn_type=1,
            external_id=1002)
        enrollment_moved = college.Enrollment.objects.create(
            student=college.Student.objects.create(external_id=1000),
            class_instance=self.class_instance,
            external_id=1000)
        enrollment_stays = college.Enrollment.objects.create(
            student=college.Student.objects.create(external_id=1001),
            class_instance=new_instance,
            external_id=1001)
        enrollment_deleted = college.Enrollment.objects.create(
            student=college.Student.objects.create(external_id=1002),
            class_instance=new_instance,
            external_id=1002)

        sync._upstream_sync_class_instance(upstream, 200, self.class_, False)

        turn_moved.refresh_from_db()
        turn_stays.refresh_from_db()
        turn_deleted.refresh_from_db()
        enrollment_moved.refresh_from_db()
        enrollment_stays.refresh_from_db()
        enrollment_deleted.refresh_from_db()

        self.assertFalse(turn_moved.disappeared)
        self.assertFalse(turn_stays.disappeared)
        self.assertTrue(turn_deleted.disappeared)
        self.assertFalse(enrollment_moved.disappeared)
        self.assertFalse(enrollment_stays.disappeared)
        self.assertTrue(enrollment_deleted.disappeared)
        self.assertEquals(turn_moved.class_instance, self.class_instance)
        self.assertEquals(turn_stays.class_instance, new_instance)
        self.assertEquals(turn_deleted.class_instance, new_instance)
        self.assertEquals(enrollment_moved.class_instance, self.class_instance)
        self.assertEquals(enrollment_stays.class_instance, new_instance)
        self.assertEquals(enrollment_deleted.class_instance, new_instance)

        other_class = college.Class.objects.create(name="Random class", external_id=1010)

        tweaked_upstream = upstream.copy()
        tweaked_upstream["class_id"] = other_class.external_id  # Illegal
        sync._upstream_sync_class_instance(tweaked_upstream, 200, self.class_, False)
        new_instance.refresh_from_db()
        self.assertEquals(new_instance.parent, self.class_)  # Unchanged
        tweaked_upstream["class_id"] = upstream["class_id"]  # Revert

        tweaked_upstream["info"] = {'boo': 'far'}  # Legal
        sync._upstream_sync_class_instance(tweaked_upstream, 200, self.class_, False)
        new_instance.refresh_from_db()
        self.assertEquals(new_instance.information, {'upstream': {'boo': 'far'}})  # Changed

        tweaked_upstream["period"] = 2  # Illegal
        sync._upstream_sync_class_instance(tweaked_upstream, 200, self.class_, False)
        new_instance.refresh_from_db()
        self.assertEquals(new_instance.period, 1)  # Unchanged
        tweaked_upstream["period"] = upstream["period"]  # Revert

        tweaked_upstream["year"] = 2021  # Illegal
        sync._upstream_sync_class_instance(tweaked_upstream, 200, self.class_, False)
        new_instance.refresh_from_db()
        self.assertEquals(new_instance.year, 2020)  # Unchanged
        tweaked_upstream["year"] = upstream["year"]  # Revert

    def test_turn_sync(self):
        upstream = {
            "class_instance_id": self.class_instance.external_id,
            "id": 200,
            "instances": [self.turn_instance.external_id, 2000],
            "minutes": 60,
            "number": 5,
            "restrictions": "Foo Bar",
            "state": "Aberto",
            "students": [self.student.external_id, 2000],
            "teachers": [self.teacher.external_id, 2000],
            "type": "t",
        }

        sync._upstream_sync_turn_info(upstream, 200, self.class_instance, False)
        new_turn = college.Turn.objects.get(external_id=200)
        self.assertEquals(new_turn.class_instance, self.class_instance)
        self.assertEquals(new_turn.number, upstream["number"])
        self.assertEquals(new_turn.turn_type, ctypes.TurnType.THEORETICAL)
        self.assertEquals(new_turn.instances.count(), 0)
        self.assertEquals(new_turn.students.count(), 1)
        self.assertEquals(new_turn.teachers.count(), 1)

        teacher_stay = college.Teacher.objects.create(name="Dr. Bar", external_id=2000)
        teacher_deleted = college.Teacher.objects.create(name="Dr. Baz", external_id=2001)
        student_stay = college.Student.objects.create(external_id=2000)
        student_deleted = college.Student.objects.create(external_id=2001)
        instance_stay = college.TurnInstance.objects.create(
            turn=new_turn,
            weekday=2,
            start=600,
            external_id=2000)
        instance_deleted = college.TurnInstance.objects.create(
            turn=new_turn,
            weekday=3,
            start=600,
            external_id=2001)

        upstream["instances"] = [self.turn_instance.external_id, 2000, 2001]
        upstream["students"] = [self.student.external_id, 2000, 2001]
        upstream["teachers"] = [self.teacher.external_id, 2000, 2001]
        sync._upstream_sync_turn_info(upstream, 200, self.class_instance, False)
        instance_stay.refresh_from_db()
        instance_deleted.refresh_from_db()

        self.assertTrue(new_turn.teachers.filter(id=self.teacher.id).exists())
        self.assertTrue(new_turn.teachers.filter(id=teacher_stay.id).exists())
        self.assertTrue(new_turn.teachers.filter(id=teacher_deleted.id).exists())
        self.assertTrue(college.TurnStudents.objects.filter(turn=new_turn, student=self.student.id).exists())
        self.assertTrue(college.TurnStudents.objects.filter(turn=new_turn, student=self.student.id).exists())
        self.assertEquals(instance_stay.turn, new_turn)
        self.assertEquals(instance_deleted.turn, new_turn)

        # Delete _deleted relations
        upstream["instances"] = [self.turn_instance.external_id, 2000]
        upstream["students"] = [self.student.external_id, 2000]
        upstream["teachers"] = [self.teacher.external_id, 2000]
        sync._upstream_sync_turn_info(upstream, 200, self.class_instance, False)
        instance_stay.refresh_from_db()
        instance_deleted.refresh_from_db()

        self.assertTrue(new_turn.teachers.filter(id=teacher_stay.id).exists())
        self.assertFalse(new_turn.teachers.filter(id=teacher_deleted.id).exists())
        self.assertTrue(college.TurnStudents.objects.filter(turn=new_turn, student=student_stay).exists())
        self.assertFalse(college.TurnStudents.objects.filter(turn=new_turn, student=student_deleted).exists())
        self.assertEquals(instance_stay.turn, new_turn)
        self.assertFalse(instance_stay.turn.disappeared)
        self.assertEquals(instance_deleted.turn, new_turn)
        self.assertTrue(instance_deleted.disappeared)

    # def test_disappearances(self):
    #     pass
    #
    # def test_freeze(self):
    #     pass
    #
    # def test_interference_with_non_external(self):
    #     pass
    #
    # def test_constraints(self):
    #     pass
