import re

from college.models import Building, Room, Department, Class, Turn, ClassInstance, TurnInstance, Student, TurnStudents, \
    Enrollment, Course
from clip import models as clip

import logging

logger = logging.getLogger(__name__)


def sync_classrooms():
    for clip_classroom in clip.Room.objects.all():
        if hasattr(clip_classroom, 'room'):  # Room already exists, check if details match
            room = clip_classroom.room
            update_room_details(room, clip_classroom)
        else:  # New room
            room = Room(clip_classroom=clip_classroom)
            update_room_details(room, clip_classroom)
            logger.info(f'Created classroom {room}.')


lab_exp = re.compile('[Ll]ab[.]? (?P<name>.*)$')
door_number_exp = re.compile('(?P<floor>\d)\.?(?P<door_number>\d+)')


def update_room_details(room: Room, clip_classroom: clip.Room):
    clip_building: clip.Building = clip_classroom.building
    try:
        building: Building = clip_building.building
    except Exception:
        raise Exception('Please *MANUALLY* link buildings to CLIP buildings before running this.')

    room.building = building

    if room.topology == Room.UNKNOWN:
        if 'lab' in clip_classroom.name.lower():
            room.topology = Room.LABORATORY

    if True or room.name is None or room.name.strip() == '':
        if room.topology == Room.LABORATORY:
            lab_matches = lab_exp.search(clip_classroom.name)
            if lab_matches:
                room.name = f'L{lab_matches.group("name")}'
            else:
                room.name = clip_classroom.name
        else:
            room.name = clip_classroom.name

    door_matches = door_number_exp.search(clip_classroom.name)
    if door_matches:
        if room.floor != int(door_matches.group('floor')):
            room.floor = int(door_matches.group('floor'))

        if room.door_number != int(door_matches.group('door_number')):
            room.door_number = int(door_matches.group('door_number'))
    room.save()


def sync_departments():
    institution = clip.Institution.objects.get(abbreviation='FCT')
    for clip_department in clip.Department.objects.filter(institution=institution):
        if not hasattr(clip_department, 'department'):
            corresponding_department = Department(name=clip_department.name, clip_department=clip_department)
            corresponding_department.save()
            logger.info(f'Created department {corresponding_department}.')


def sync_courses():
    clip_institution = clip.Institution.objects.get(abbreviation='FCT')
    for clip_course in clip_institution.courses.all():
        if not hasattr(clip_course, 'course'):
            if clip_course.degree is None:
                logger.warning(f'Unable to create course {clip_course} since it has no degree.')
                continue
            course = Course(name=clip_course.name,
                            degree=clip_course.degree,
                            abbreviation=clip_course.degree,
                            clip_course=clip_course)
            course.save()
            logger.info(f'Created course {course}.')


def sync_class_and_instances(year: int, period: int, bootstrap=False):
    for clip_class_instance in clip.ClassInstance.objects.filter(year=year, period=period).all():
        clip_class: clip.Class = clip_class_instance.parent

        if hasattr(clip_class, 'related_class'):  # There's a class attached to this crawled class.
            related_class = clip_class.related_class
        else:  # No corresponding class. Create one.
            related_class = Class(name=clip_class.name,
                                  clip_class=clip_class,
                                  abbreviation=clip_class.abbreviation,
                                  department=clip_class.department.department,
                                  credits=clip_class.ects)
            related_class.save()
            logger.info(f'Created class {related_class}.')

        if hasattr(clip_class_instance, 'class_instance'):  # There's a class attached to this crawled class.
            class_instance = clip_class_instance.class_instance
        else:
            class_instance = ClassInstance(parent=related_class,
                                           period=period,
                                           year=year,
                                           clip_class_instance=clip_class_instance)
            class_instance.save()
            logger.info(f'Created class instance {class_instance}.')

        if bootstrap:
            sync_turns(class_instance, bootstrap=True)


def sync_turns(class_instance: ClassInstance, bootstrap=False):
    for clip_turn in class_instance.clip_class_instance.turns.all():
        if hasattr(clip_turn, 'turn'):  # There is already a turn for this crawled turn.
            turn: Turn = clip_turn.turn
        else:  # No corresponding turn. Create one.
            turn = Turn(clip_turn=clip_turn,
                        turn_type=clip_turn.type,
                        number=clip_turn.number,
                        class_instance=class_instance)
            logger.info(f'Created turn {turn}.')
            turn.save()

        if bootstrap:
            sync_turn_instances(turn)


def sync_turn_instances(turn: Turn):
    for clip_turn_instance in turn.clip_turn.instances.all():
        if hasattr(clip_turn_instance, 'turn_instance'):
            turn_instance = clip_turn_instance.turn_instance
            if hasattr(clip_turn_instance, 'classroom'):
                if turn_instance.room != clip_turn_instance.classroom.room:
                    logger.warning(f'Turn instance {turn_instance} changed '
                                   f'from {turn_instance.room} to {clip_turn_instance.classroom.room}.')
                    turn_instance.room = clip_turn_instance.classroom.room
                    turn_instance.save()

        else:
            if clip_turn_instance.start and clip_turn_instance.end:
                duration = clip_turn_instance.end - clip_turn_instance.start
            else:
                duration = None

            if hasattr(clip_turn_instance, 'classroom'):  # There is already a turn instance for this crawled instance.
                # ...  ClipTurnInstance.ClipClassroom.Room
                room = clip_turn_instance.classroom.room
            else:  # No corresponding turn instance. Create one.
                room = None

            turn_instance = TurnInstance(turn=turn,
                                         clip_turn_instance=clip_turn_instance,
                                         weekday=clip_turn_instance.weekday,
                                         start=clip_turn_instance.start,
                                         duration=duration,
                                         room=room)
            turn_instance.save()
            logger.info(f'Created turn instance {turn_instance}.')


def create_student(clip_student: clip.Student) -> Student:
    if hasattr(clip_student, 'student'):
        student = clip_student.student
        logger.warning(f"Attempted to create a student which already exists ({student}).")
        return student

    student = Student(number=int(clip_student.iid),
                      abbreviation=clip_student.abbreviation,
                      course=clip_student.course.course,
                      clip_student=clip_student)
    student.save()
    sync_student_enrollments(student)
    return student


def sync_student_enrollments(student: Student):
    for clip_enrollment in clip.Enrollment.objects.filter(student=student.clip_student).all():
        if not hasattr(clip_enrollment, 'enrollment'):
            class_instance = clip_enrollment.class_instance.class_instance
            Enrollment(student=student, class_instance=class_instance, clip_enrollment=clip_enrollment).save()
            logger.info(f'Enrolled student {student} to {class_instance}.')
    sync_student_turns(student)


def sync_student_turns(student: Student):
    for clip_turn in clip.Turn.objects.filter(students=student.clip_student).all():
        if clip_turn.turn not in student.turns.all():
            TurnStudents(student=student, turn=clip_turn.turn).save()
            logger.info(f'Added turn {clip_turn.turn} to student {student}.')
    # TODO delete old turns
