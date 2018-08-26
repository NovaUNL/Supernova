import re

from . import models as m
from clip import models as clip

import logging

logger = logging.getLogger(__name__)


def rooms():
    populated = m.Room.objects.exists()
    for clip_room in clip.Room.objects.all():
        if hasattr(clip_room, 'room'):  # Room already exists, check if details match
            room = clip_room.room
            update_room_details(room, clip_room)
        else:  # New room
            if hasattr(clip_room.building, 'building'):
                building = clip_room.building.building
            else:
                logger.info(f"Skipped room {clip_room}")
                continue

            if populated:
                confirmation = input(f"Type 'yes' to add new room {clip_room} (ignored otherwise)")
                if confirmation == 'yes':
                    room = m.Room(type=clip_room.room_type, building=building, clip_room=clip_room)
                    update_room_details(room, clip_room)
                    logger.info(f'Created room {room}.')
            else:
                room = m.Room(type=clip_room.room_type, building=building, clip_room=clip_room)
                update_room_details(room, clip_room)
                logger.info(f'Created room {room}.')


door_number_exp = re.compile('(?P<floor>\d)\.?(?P<door_number>\d+)')


def update_room_details(room: m.Room, clip_room: clip.Room):
    clip_building: clip.Building = clip_room.building
    try:
        building: m.Building = clip_building.building
    except Exception:
        raise Exception('Please *MANUALLY* link buildings to CLIP buildings before running this.')

    room.building = building

    room.name = clip_room.name
    room.type = clip_room.room_type

    door_matches = door_number_exp.search(clip_room.name)
    if door_matches:
        if room.floor != int(door_matches.group('floor')):
            room.floor = int(door_matches.group('floor'))

        if room.door_number != int(door_matches.group('door_number')):
            room.door_number = int(door_matches.group('door_number'))
    room.save()


def departments():
    institution = clip.Institution.objects.get(abbreviation='FCT')
    for clip_department in clip.Department.objects.filter(institution=institution):
        if not hasattr(clip_department, 'department'):
            corresponding_department = m.Department(name=clip_department.name, clip_department=clip_department)
            corresponding_department.save()
            logger.info(f'Created department {corresponding_department}.')


def courses():
    clip_institution = clip.Institution.objects.get(abbreviation='FCT')
    for clip_course in clip_institution.courses.all():
        if not hasattr(clip_course, 'course'):
            if clip_course.degree is None:
                logger.warning(f'Unable to create course {clip_course} since it has no degree.')
                continue
            course = m.Course(
                name=clip_course.name,
                degree=clip_course.degree,
                abbreviation=clip_course.degree,
                clip_course=clip_course)
            course.save()
            logger.info(f'Created course {course}.')


def teachers():
    for department in m.Department.objects.all():
        clip_department = department.clip_department
        for clip_teacher in clip_department.teachers.all():
            if m.Teacher.objects.filter(iid=clip_teacher.iid).count() == 0:
                teacher = m.Teacher(iid=clip_teacher.iid, name=clip_teacher.name)
                teacher.save()
                logger.info(f'Created teacher {teacher}')
            else:
                teacher = m.Teacher.objects.get(iid=clip_teacher.iid)

            if clip_teacher not in teacher.clip_teachers.all():
                teacher.clip_teachers.add(clip_teacher)
                logger.info(f"{clip_teacher} matched with {teacher}")

            if department not in teacher.departments.all():
                teacher.departments.add(department)
                logger.info(f"Added {department} to teacher {teacher}")


def class_and_instances(year: int, period: int, bootstrap=False):
    for clip_class_instance in clip.ClassInstance.objects.filter(year=year, period=period).all():
        clip_class: clip.Class = clip_class_instance.parent

        if hasattr(clip_class, 'related_class'):  # There's a class attached to this crawled class.
            related_class = clip_class.related_class
        else:  # No corresponding class. Create one.
            related_class = m.Class(
                name=clip_class.name,
                clip_class=clip_class,
                abbreviation=clip_class.abbreviation,
                department=clip_class.department.department,
                credits=clip_class.ects)
            related_class.save()
            logger.info(f'Created class {related_class}.')

        if hasattr(clip_class_instance, 'class_instance'):  # There's a class attached to this crawled class.
            class_instance = clip_class_instance.class_instance
        else:
            information = generate_class_instance_information(clip_class_instance)
            class_instance = m.ClassInstance(
                parent=related_class,
                period=period,
                year=year,
                clip_class_instance=clip_class_instance,
                information=information)
            class_instance.save()
            logger.info(f'Created class instance {class_instance}.')

        if bootstrap:
            turns(class_instance, bootstrap=True)


def turns(class_instance: m.ClassInstance, bootstrap=False):
    for clip_turn in class_instance.clip_class_instance.turns.all():
        if hasattr(clip_turn, 'turn'):  # There is already a turn for this crawled turn.
            turn: m.Turn = clip_turn.turn
        else:  # No corresponding turn. Create one.
            turn = m.Turn(
                clip_turn=clip_turn,
                turn_type=clip_turn.type,
                number=clip_turn.number,
                class_instance=class_instance)
            logger.info(f'Created turn {turn}.')
            turn.save()

        if bootstrap:
            turn_instances(turn)


def turn_instances(turn: m.Turn):
    for clip_turn_instance in turn.clip_turn.instances.all():
        if hasattr(clip_turn_instance, 'turn_instance'):
            turn_instance = clip_turn_instance.turn_instance
            if hasattr(clip_turn_instance, 'room'):
                if turn_instance.room != clip_turn_instance.room.room:
                    logger.warning(f'Turn instance {turn_instance} changed '
                                   f'from {turn_instance.room} to {clip_turn_instance.room.room}.')
                    turn_instance.room = clip_turn_instance.room.room
                    turn_instance.save()

        else:
            if clip_turn_instance.start and clip_turn_instance.end:
                duration = clip_turn_instance.end - clip_turn_instance.start
            else:
                duration = None

            if hasattr(clip_turn_instance, 'room'):  # There is already a turn instance for this crawled instance.
                # ...  ClipTurnInstance.ClipRoom.Room
                room = clip_turn_instance.room.room
            else:  # No corresponding turn instance. Create one.
                room = None

            turn_instance = m.TurnInstance(
                turn=turn,
                clip_turn_instance=clip_turn_instance,
                weekday=clip_turn_instance.weekday,
                start=clip_turn_instance.start,
                duration=duration,
                room=room)
            turn_instance.save()
            logger.info(f'Created turn instance {turn_instance}.')


def create_student(clip_student: clip.Student) -> m.Student:
    if hasattr(clip_student, 'student'):
        student = clip_student.student
        logger.warning(f"Attempted to create a student which already exists ({student}).")
        return student

    courses = clip_student.courses.all()
    if len(courses) == 1:
        clip_course: clip.Course = courses[0]
        course = clip_course.course
    else:
        course = None

    student = m.Student(
        number=clip_student.iid,
        abbreviation=clip_student.abbreviation,
        course=course,
        graduation_grade=clip_student.graduation_grade,
        clip_student=clip_student)
    student.save()
    student_enrollments(student)
    return student


def student_enrollments(student: m.Student):
    for clip_enrollment in clip.Enrollment.objects.filter(student=student.clip_student).all():
        if not hasattr(clip_enrollment, 'enrollment'):
            class_instance = clip_enrollment.class_instance.class_instance
            m.Enrollment(student=student, class_instance=class_instance, clip_enrollment=clip_enrollment).save()
            logger.info(f'Enrolled student {student} to {class_instance}.')
    student_turns(student)


def student_turns(student: m.Student):
    for clip_turn in clip.Turn.objects.filter(students=student.clip_student).all():
        if clip_turn.turn not in student.turns.all():
            m.TurnStudents(student=student, turn=clip_turn.turn).save()
            logger.info(f'Added turn {clip_turn.turn} to student {student}.')
    # TODO delete old turns


# Helper functions

def generate_class_instance_information(clip_instance: clip.ClassInstance) -> dict:
    """
    Generates the class instance information dictionary
    :param clip_instance: :py:class:`clip.ClassInstance`
    :return: Dictionary with the information fields
    """
    information = {}
    if clip_instance.description_pt is not None:
        information['description'] = {
            'pt': clip_instance.description_pt,
            'en': clip_instance.description_en,
            'edited_datetime': clip_instance.description_edited_datetime,
            'editor': clip_instance.description_editor}

    if clip_instance.objectives_pt is not None:
        information['objectives'] = {
            'pt': clip_instance.objectives_pt,
            'en': clip_instance.objectives_en,
            'edited_datetime': clip_instance.objectives_edited_datetime,
            'editor': clip_instance.objectives_editor}

    if clip_instance.requirements_pt is not None:
        information['requirements'] = {
            'pt': clip_instance.requirements_pt,
            'en': clip_instance.requirements_en,
            'edited_datetime': clip_instance.requirements_edited_datetime,
            'editor': clip_instance.requirements_editor}

    if clip_instance.competences_pt is not None:
        information['competences'] = {
            'pt': clip_instance.competences_pt,
            'en': clip_instance.competences_en,
            'edited_datetime': clip_instance.competences_edited_datetime,
            'editor': clip_instance.competences_editor}

    if clip_instance.program_pt is not None:
        information['program'] = {
            'pt': clip_instance.program_pt,
            'en': clip_instance.program_en,
            'edited_datetime': clip_instance.program_edited_datetime,
            'editor': clip_instance.program_editor}

    if clip_instance.bibliography_pt is not None:
        information['bibliography'] = {
            'pt': clip_instance.bibliography_pt,
            'en': clip_instance.bibliography_en,
            'edited_datetime': clip_instance.bibliography_edited_datetime,
            'editor': clip_instance.bibliography_editor}

    if clip_instance.assistance_pt is not None:
        information['assistance'] = {
            'pt': clip_instance.assistance_pt,
            'en': clip_instance.assistance_en,
            'edited_datetime': clip_instance.assistance_edited_datetime,
            'editor': clip_instance.assistance_editor}

    if clip_instance.assistance_pt is not None:
        information['teaching'] = {
            'pt': clip_instance.teaching_methods_pt,
            'en': clip_instance.teaching_methods_en,
            'edited_datetime': clip_instance.teaching_methods_edited_datetime,
            'editor': clip_instance.teaching_methods_editor}

    if clip_instance.teaching_methods_pt is not None:
        information['teaching'] = {
            'pt': clip_instance.teaching_methods_pt,
            'en': clip_instance.teaching_methods_en,
            'edited_datetime': clip_instance.teaching_methods_edited_datetime,
            'editor': clip_instance.teaching_methods_editor}

    if clip_instance.evaluation_methods_pt is not None:
        information['evaluation'] = {
            'pt': clip_instance.evaluation_methods_pt,
            'en': clip_instance.evaluation_methods_en,
            'edited_datetime': clip_instance.evaluation_methods_edited_datetime,
            'editor': clip_instance.evaluation_methods_editor}
    if clip_instance.extra_info_pt is not None:
        information['extra'] = {
            'pt': clip_instance.extra_info_pt,
            'en': clip_instance.extra_info_en,
            'edited_datetime': clip_instance.extra_info_edited_datetime,
            'editor': clip_instance.extra_info_editor}

    if clip_instance.working_hours is not None:
        information['working_hours'] = clip_instance.working_hours

    return information
