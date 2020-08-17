from django.test import TestCase

from college import models as college
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
        upstream = {
            "abbr": "New",
            "dept": self.department.external_id,
            "ects": 12,
            "id": 201,
            "iid": 201,
            "instances": [100, 1001],
            "name": "New Class"
        }

        sync._upstream_sync_class(upstream, 201, self.department, False)

        new_class = college.Class.objects.get(external_id=201)

        self.assertEquals(new_class.name, "New Class")
        self.assertEquals(new_class.abbreviation, "New")
        self.assertEquals(new_class.credits, 12)
        self.assertEquals(new_class.department, self.department)

        # Stays
        a = college.ClassInstance.objects.create(
            parent=new_class,
            year=2020,
            period=2,
            external_id=1001,
            information=dict())
        # Gets deleted
        b = college.ClassInstance.objects.create(
            parent=new_class,
            year=2020,
            period=3,
            external_id=1002,
            information=dict())

        sync._upstream_sync_class(upstream, 201, self.department, False)
        a.refresh_from_db()
        b.refresh_from_db()

        self.assertEquals(a.parent, new_class)
        self.assertFalse(a.disappeared)
        self.assertTrue(b.disappeared)
        self.assertTrue(a in new_class.instances.all())
        self.assertTrue(b in new_class.instances.all())

        other_dept = college.Department.objects.create(name="Default", external_id=1001)
        upstream = {
            "abbr": "Newr",
            "dept": other_dept.external_id,
            "ects": 15,
            "id": 201,
            "iid": 201,
            "instances": [100, 1002],
            "name": "Newer Class"
        }

        sync._upstream_sync_class(upstream, 201, self.department, False)
        new_class.refresh_from_db()
        a.refresh_from_db()
        b.refresh_from_db()

        self.assertEquals(new_class.name, "Newer Class")
        self.assertEquals(new_class.abbreviation, "Newr")
        self.assertEquals(new_class.credits, 15)
        self.assertEquals(new_class.department, other_dept)
        self.assertEquals(a.parent, new_class)
        self.assertTrue(a.disappeared)
        self.assertFalse(b.disappeared)
        self.assertTrue(a in new_class.instances.all())
        self.assertTrue(b in new_class.instances.all())

    # def test_disappearances(self):
    #     pass
    #
    # def test_freeze(self):
    #     pass
