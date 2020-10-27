import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from users import models as m
from college import models as college

logger = logging.getLogger(__name__)


def student_assignment(user: m.User, student: college.Student):
    if student.user is not None and student.user != student:
        logging.warning(f"Student {student.number}({student.abbreviation}) "
                        f"being disconnected from user {user.username}({user.nickname})")
    logging.info(f"Student {student.number}({student.abbreviation}) "
                 f"being attached to user {user.username}({user.nickname})")
    student.user = user
    student_access = Permission.objects.get(
        codename='student_access',
        content_type=ContentType.objects.get_for_model(m.User))
    if student_access not in user.user_permissions.all():
        user.user_permissions.add(student_access)
        logger.info(f"User {user.username}({user.nickname}) was granted student access")

    user.calculate_missing_info()
    user.updated_cached()
    student.update_progress_info()
    student.save()


def teacher_assignment(user: m.User, teacher: college.Teacher):
    if teacher.user is not None and teacher.user != teacher:
        logging.warning(f"Teacher {teacher.name}({teacher.abbreviation}) "
                        f"being disconnected from user {user.username}({user.nickname})")
    logging.info(f"Teacher {teacher.name}({teacher.abbreviation}) "
                 f"being attached to user {user.username}({user.nickname})")
    teacher.user = user
    student_access = Permission.objects.get(
        codename='student_access',
        content_type=ContentType.objects.get_for_model(m.User))
    teacher_access = Permission.objects.get(
        codename='teacher_access',
        content_type=ContentType.objects.get_for_model(m.User))

    if student_access not in user.user_permissions.all():
        user.user_permissions.add(student_access)
        logger.info(f"User {user.username}({user.nickname}) was granted student access")

    if teacher_access not in user.user_permissions.all():
        user.user_permissions.add(teacher_access)
        logger.info(f"User {user.username}({user.nickname}) was granted teacher access")

    user.calculate_missing_info()
    user.updated_cached()
    teacher.update_yearspan()
    teacher.save()
