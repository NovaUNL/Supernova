from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from users import models as m
from college import models as college


def on_student_assignment(user: m.User, student: college.Student):
    student_access = Permission.objects.get(
        codename='student_access',
        content_type=ContentType.objects.get_for_model(m.User))
    user.user_permissions.add(student_access)
    user.calculate_missing_info()
    user.updated_cached()
    student.update_progress_info()
    student.save()


def on_teacher_assignment(user: m.User, teacher: college.Teacher):
    student_access = Permission.objects.get(
        codename='student_access',
        content_type=ContentType.objects.get_for_model(m.User))
    teacher_access = Permission.objects.get(
        codename='teacher_access',
        content_type=ContentType.objects.get_for_model(m.User))
    user.user_permissions.add(student_access)
    user.user_permissions.add(teacher_access)
    user.calculate_missing_info()
    user.updated_cached()
    teacher.update_yearspan()
    teacher.save()
