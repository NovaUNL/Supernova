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
