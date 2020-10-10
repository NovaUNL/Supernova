import re
from datetime import date, datetime
import requests
import logging

from django.utils import timezone
from django.utils.timezone import make_aware

from django.core.exceptions import ObjectDoesNotExist

from settings import CLIPY

from college import models as m
from college import choice_types as ctypes
from supernova.utils import correlation

logger = logging.getLogger(__name__)


# TODO deduplicate code in _request methods
# TODO deduplicate code in relationships

def assert_buildings_inserted():
    ignored = {2, 1191, 1197, 1198, 1632, 1653}
    r = requests.get("http://%s/buildings/" % CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch buildings")
    clip_buildings = r.json()
    ids = set(map(lambda item: item['id'], clip_buildings))
    missing = ids.difference(set(m.Building.objects.values_list('external_id', flat=True)))
    missing = missing.difference(ignored)
    for building in clip_buildings:
        if building['id'] in missing:
            logger.info(f'Building {building} missing.')


door_number_exp = re.compile('(?P<floor>\d)\.?(?P<door_number>\d+)')


def sync_rooms():
    """
    Fetches the most recent available info about rooms.
    Creates missing rooms.
    """
    r = requests.get("http://%s/rooms/" % CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch rooms")

    existing = {room.external_id: room for room in m.Room.objects.all()}
    for clip_room in r.json():
        building = m.Building.objects.filter(external_id=clip_room['building']).first()
        if building is None:
            logger.info(f"Skipped room {clip_room}")
            continue

        room = existing.get(clip_room['id'])
        if room is None:  # New room
            room = m.Room(
                name=clip_room['name'],
                type=clip_room["type"],
                building=building,
                external_id=clip_room['id'],
                iid=clip_room['id'],
                frozen=False,
                external_update=make_aware(datetime.now()))
            logger.info(f'Created room {room}.')
        else:
            logger.debug(f'Room {room} already exists.')
            if not room.frozen:
                if room.building != building:
                    logger.warning(f'Building for room {room} changed to building {building}.')
                    room.building = building

                if room.name != clip_room["name"]:
                    logger.warning(f'Room {room} changed name to {clip_room["name"]}.')
                    room.name = clip_room["name"]

                if room.type != clip_room["type"]:
                    logger.warning(f'Room {room} type changed to {clip_room["type"]}.')
                    # room.type = clip_room["type"] TODO uncomment after freezing manually changed rooms

        if not room.frozen:
            door_matches = door_number_exp.search(clip_room['name'])
            if door_matches:
                room.floor = int(door_matches.group('floor'))
                room.door_number = int(door_matches.group('door_number'))
            room.external_update = make_aware(datetime.now())

        room.save()


def sync_departments(recurse=False):
    upstream = _request_departments()
    _upstream_sync_departments(upstream, recurse)


def _request_departments():
    r = requests.get("http://%s/departments/" % CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch departments")
    return r.json()


def _upstream_sync_departments(upstream, recurse):
    current = m.Department.objects.exclude(external_id=None).all()
    clip_ids = {entry['id'] for entry in upstream}
    new, disappeared, mirrored = _upstream_diff(set(current), clip_ids)

    disappeared_departments = m.Department.objects.filter(external_id__in=disappeared)
    for department in disappeared_departments.all():
        logger.warning(f"Department {department.name} disappeared")
    disappeared_departments.update(disappeared=True, external_update=make_aware(datetime.now()))
    m.Department.objects.filter(external_id__in=mirrored).update(external_update=make_aware(datetime.now()))

    for clip_department in upstream:
        if clip_department['id'] in new:
            department = m.Department.objects.create(
                name=clip_department['name'],
                iid=clip_department['id'],
                external_id=clip_department['id'],
                frozen=False,
                external_update=make_aware(datetime.now()))
            logger.info(f'Created department {clip_department}.')
            if recurse:
                sync_department(department, recurse=True)


def sync_department(department, recurse=False):
    """
    Sync the information in a department
    :param department: The department that is being sync'd
    :param recurse: Whether to recurse to the derivative entities (classes)
    """
    upstream = _request_department(department)
    _upstream_sync_department(upstream, department, recurse)


def _request_department(department):
    r = requests.get(f"http://{CLIPY['host']}/department/{department.external_id}")
    if r.status_code != 200:
        raise Exception(f"Unable to fetch department {department.external_id}")
    return r.json()


def _upstream_sync_department(upstream, department, recurse=False):
    # ---------  Related classes ---------
    classes = department.classes.exclude(external_id=None).all()
    new, disappeared, mirrored = _upstream_diff(set(classes), set(upstream['classes']))

    if recurse:
        for ext_id in new:
            sync_class(ext_id, recurse=True, department=department)

    m.Class.objects.filter(external_id__in=new).update(department=department)
    m.Class.objects.filter(external_id__in=mirrored).update(external_update=make_aware(datetime.now()))
    m.Class.objects.filter(external_id__in=disappeared).update(department=None)
    disappeared = m.Class.objects.filter(external_id__in=disappeared)
    for klass in disappeared.all():
        logger.warning(f"{klass} removed from {department}.")

    # ---------  Related teachers ---------
    # Handled in the teacher function


def sync_classes(recurse=False):
    upstream = _request_classes()
    _upstream_sync_classes(upstream, recurse)


def _request_classes():
    r = requests.get("http://%s/classes/" % CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch classes")
    return r.json()


def _upstream_sync_classes(upstream, recurse):
    known_ids = set(m.Class.objects.exclude(external_id=None).values_list('external_id', flat=True))
    clip_ids = {entry['id'] for entry in upstream}
    disappeared = known_ids.difference(clip_ids)
    mirrored = known_ids.intersection(clip_ids)

    disappeared_classes = m.Class.objects.filter(external_id__in=disappeared)
    for klass in disappeared_classes.all():
        logger.warning(f"Class {klass.name} disappeared")
    disappeared_classes.update(disappeared=True, external_update=make_aware(datetime.now()))
    m.Class.objects.filter(external_id__in=mirrored).update(external_update=make_aware(datetime.now()))

    for clip_class in upstream:
        if clip_class['id'] not in disappeared:
            _upstream_sync_class(clip_class, clip_class['id'], recurse)


def sync_class(external_id, recurse=False):
    """
    Sync the information in a class
    :param external_id: The foreign id of the class that is being sync'd
    :param department: The parent department of this class (optional)
    :param recurse: Whether to recurse to the derivative entities (class instances)
    """
    upstream = _request_class(external_id)
    _upstream_sync_class(upstream, external_id, recurse)


def _request_class(external_id):
    r = requests.get(f"http://{CLIPY['host']}/class/{external_id}")
    if r.status_code != 200:
        raise Exception("Unable to fetch class")
    return r.json()


def _upstream_sync_class(upstream, external_id, recurse):
    try:
        obj = m.Class.objects.get(external_id=external_id)
        if not obj.frozen:
            changed = False
            if upstream['name'] != obj.name:
                logger.warning(f"Class {obj} name changed from {obj.name} to {upstream['name']}")
                obj.name = upstream['name']
                changed = True
            if upstream['abbr'] != obj.abbreviation:
                logger.warning(f"Class {obj} abbreviation changed from {obj.abbreviation} to {upstream['abbr']}")
                obj.abbreviation = upstream['abbr']
                changed = True
            if upstream['ects'] != obj.credits:
                logger.warning(f"Class {obj} credits changed from {obj.credits} to {upstream['ects']}")
                obj.credits = upstream['ects']
                changed = True
            if changed:
                obj.save()
    except ObjectDoesNotExist:
        obj = m.Class.objects.create(
            name=upstream['name'],
            abbreviation=upstream['abbr'],
            credits=upstream['ects'],
            iid=upstream['id'],
            external_id=external_id,
            frozen=False,
            external_update=make_aware(datetime.now()))
        logger.info(f"Created class {obj}")

    # ---------  Related Instances ---------
    instances = obj.instances.exclude(external_id=None).all()

    new, disappeared, mirrored = _upstream_diff(set(instances), set(upstream['instances']))

    # Class instances do not simply move to another class
    if m.ClassInstance.objects.filter(external_id__in=new).exists():
        logger.critical(f"Some instances of class {obj} belong to another class: {new}")

    if recurse:
        for ext_id in new:
            sync_class_instance(ext_id, recurse=True, klass=obj)

    m.ClassInstance.objects.filter(external_id__in=mirrored). \
        update(disappeared=False, external_update=make_aware(datetime.now()))
    m.ClassInstance.objects.filter(external_id__in=disappeared).update(disappeared=True)
    disappeared = m.ClassInstance.objects.filter(external_id__in=disappeared)
    for instance in disappeared.all():
        logger.warning(f"{instance} removed from {obj}.")


def sync_class_instance(external_id, klass=None, recurse=False):
    """
    Sync the information in a class instance
    :param external_id: The foreign id of the class instance that is being sync'd
    :param klass: The class that is parent this class instance (optional)
    :param recurse: Whether to recurse to the derivative entities (shifts, enrollments and evaluations)
    """
    upstream = _request_class_instance(external_id)
    _upstream_sync_class_instance(upstream, external_id, klass, recurse)


def _request_class_instance(external_id):
    r = requests.get(f"http://{CLIPY['host']}/class_inst/{external_id}")
    if r.status_code != 200:
        raise Exception(f"Unable to fetch class instance {external_id}")
    return r.json()


def _upstream_sync_class_instance(upstream, external_id, klass, recurse):
    if klass is None:
        klass = m.Class.objects.get(external_id=upstream['class_id'])

    try:
        department = m.Department.objects.get(external_id=upstream['department_id'])
    except m.Department.DoesNotExist:
        logger.error(f"Class instance {external_id} belongs to unknown department ({upstream['department_id']}")
        return

    try:
        obj = m.ClassInstance.objects.get(parent=klass, external_id=external_id)
        if not obj.frozen:
            changed = False
            if upstream['year'] != obj.year:
                logger.error(f"Instance {obj} year remotely changed from {obj.year} to {upstream['year']}")
                # obj.year = upstream['year']
                # changed = True

            if upstream['period'] != obj.period:
                logger.error(f"Instance {obj} period remotely changed from {obj.period} to {upstream['period']}")
                # obj.period = upstream['period']
                # changed = True

            if obj.information is None:
                obj.information = {'upstream': upstream['info']}
                changed = True
            elif 'upstream' not in obj.information or obj.information['upstream'] != upstream['info']:
                obj.information['upstream'] = upstream['info']
                changed = True

            if changed:
                obj.save()
    except ObjectDoesNotExist:
        obj = m.ClassInstance.objects.create(
            parent=klass,
            year=upstream['year'],
            period=upstream['period'],
            department=department,
            external_id=external_id,
            information={'upstream': upstream['info']},
            frozen=False,
            external_update=timezone.now())
        logger.info(f"Class instance {obj} created")
        if klass.department != department:
            if klass.instances.order_by('year', 'period').reverse().first() == obj:
                logger.warning(f'Changed class {klass} department from {klass.department} to {department}')
                klass.department = department
                klass.save()

    # ---------  Related shifts ---------
    shifts = obj.shifts.exclude(external_id=None).all()

    new, disappeared, mirrored = _upstream_diff(set(shifts), set(upstream['shifts']))

    if m.Shift.objects.filter(external_id__in=new).exists():
        logger.critical(f"Some shifts of class instance {obj} belong to another instance: {new}")

    if recurse:
        for ext_id in new:
            sync_shift(ext_id, recurse=True, class_inst=obj)

    m.Shift.objects \
        .filter(external_id__in=mirrored). \
        update(disappeared=False, external_update=make_aware(datetime.now()))
    m.Shift.objects.filter(external_id__in=disappeared).update(disappeared=True)
    disappeared = m.Shift.objects.filter(external_id__in=disappeared)
    for shift in disappeared.all():
        logger.warning(f"{shift} removed from {obj}.")

    events = obj.events.exclude(external_id=None).all()
    upstream_events = {event['id']: event for event in upstream['events']}
    new, disappeared, mirrored = _upstream_diff(set(events), set(upstream_events.keys()))

    if recurse:
        for ext_id in new:
            upstream_data = upstream_events[ext_id]
            _upstream_sync_event(upstream_data, ext_id, class_inst=obj)

    m.ClassInstanceEvent.objects.filter(external_id__in=mirrored). \
        update(disappeared=False, external_update=make_aware(datetime.now()))
    m.ClassInstanceEvent.objects.filter(external_id__in=disappeared).update(disappeared=True)
    disappeared = m.ClassInstanceEvent.objects.filter(external_id__in=disappeared)
    for event in disappeared.all():
        logger.warning(f"{event} removed from {obj}.")

    # ---------  Related enrollments ---------
    enrollments = obj.enrollments.exclude(external_id=None).all()

    new, disappeared, mirrored = _upstream_diff(set(enrollments), set(upstream['enrollments']))

    if m.Enrollment.objects.filter(external_id__in=new).exists():
        logger.critical(f"Some enrollments of class instance {obj} belong to another instance: {new}")

    if recurse:
        for ext_id in new:
            sync_enrollment(ext_id, class_inst=obj)

    m.Enrollment.objects.filter(external_id__in=mirrored). \
        update(disappeared=False, external_update=make_aware(datetime.now()))
    m.Enrollment.objects.filter(external_id__in=disappeared).update(disappeared=True)
    disappeared = m.Enrollment.objects.filter(external_id__in=disappeared)
    for enrollment in disappeared.all():
        logger.warning(f"{enrollment} removed from {obj}.")

    # ---------  OTHER TODO ---------
    if recurse:
        # Must happen after the shift sync to have the teachers known
        sync_class_instance_files(external_id, class_inst=obj)
    # TODO
    # evaluations = obj.enrollments.exclude(external_id=None).all()
    # _related(evaluations, upstream['evaluations'], sync_evaluation, m.ClassEvaluation, recurse, class_inst=obj)


def sync_class_instance_files(external_id, class_inst):
    """
    Sync the file information in a class instance
    :param external_id: The foreign id of the class instance that is being sync'd
    :param class_inst: The class instance (optional)
    """
    upstream = _request_class_instance_files(external_id)
    _upstream_sync_class_instance_files(upstream, external_id, class_inst)


def _request_class_instance_files(external_id):
    r = requests.get(f"http://{CLIPY['host']}/files/{external_id}")
    if r.status_code != 200:
        raise Exception("Unable to fetch class instance files")
    return r.json()


def _upstream_sync_class_instance_files(upstream, external_id, class_inst):
    if class_inst is None:
        class_inst = m.ClassInstance.objects.prefetch_related('files__file').get(external_id=external_id)

    upstream = {entry['hash']: entry for entry in upstream}
    upstream_ids = set(upstream.keys())
    downstream_files = {ifile.file.hash: ifile for ifile in class_inst.files.all()}
    downstream_ids = set(downstream_files.keys())
    new = upstream_ids.difference(downstream_ids)
    removed = downstream_ids.difference(upstream_ids)
    mirrored = downstream_ids.intersection(upstream_ids)
    teachers = {teacher.name: teacher for teacher in m.Teacher.objects.filter(shifts__class_instance=class_inst).all()}

    for hash in mirrored:
        upsteam_info = upstream[hash]
        downstream_file: m.ClassFile = downstream_files[hash]
        changed = False
        if downstream_file.name != (name := upsteam_info['name']):
            logger.warning(f"{downstream_file} name changed to {name}")
            downstream_file.name = name
            changed = True
        upstream_date = make_aware(datetime.fromisoformat(upsteam_info['upload_datetime']), is_dst=True)
        if downstream_file.upload_datetime != upstream_date:
            logger.warning(f"{downstream_file} upload date changed "
                           f"from {downstream_file.upload_datetime} to {upstream_date}")
            downstream_file.upload_datetime = upstream_date
            changed = True

        uploader_teacher = _closest_teacher(teachers, upsteam_info['uploader'])
        if downstream_file.uploader_teacher != uploader_teacher:
            logger.warning(f"{downstream_file} uploader changed "
                           f"from {downstream_file.uploader_teacher} to {uploader_teacher}")
            downstream_file.uploader_teacher = uploader_teacher
            changed = True
        if changed:
            downstream_file.save()

    for ifile in class_inst.files.filter(file__hash__in=removed):
        logger.warning(f"File {ifile} removed from {class_inst}")
        ifile.delete()
        continue

    for hash in new:
        upsteam_info = upstream[hash]
        uploader_teacher = _closest_teacher(teachers, upsteam_info['uploader'])

        try:
            file = m.File.objects.get(hash=upsteam_info['hash'])
        except ObjectDoesNotExist:
            file = m.File.objects.create(
                size=upsteam_info['size'],
                hash=upsteam_info['hash'],
                mime=upsteam_info['mime'],
                external_id=upsteam_info['id'],
                # Obs: Files are being identified by hash, so there might be ignored IDs
                iid=upsteam_info['id'])
            logger.info(f"File {file} created")

        if not m.ClassFile.objects.filter(file=file, class_instance=class_inst).exists():
            m.ClassFile.objects.create(
                file=file,
                class_instance=class_inst,
                type=upsteam_info['type'],
                name=upsteam_info['name'],
                upload_datetime=make_aware(datetime.fromisoformat(upsteam_info['upload_datetime']), is_dst=True),
                uploader_teacher=uploader_teacher)
            logger.info(f"File {file} added to class {class_inst}")


def sync_enrollment(external_id, class_inst=None):
    """
    Sync the information in an enrollment
    :param external_id: The foreign id of the enrollment that is being sync'd
    :param class_inst: The class instance (optional)
    :return:
    """
    upstream = _request_enrollment(external_id)
    if upstream is None:
        logger.critical("Deleted enrollment attempted to sync")
        return
    _upstream_sync_enrollment(upstream, external_id, class_inst)


def _request_enrollment(external_id):
    r = requests.get(f"http://{CLIPY['host']}/enrollment/{external_id}")
    if r.status_code != 200:
        raise Exception(f"Unable to fetch enrollment {external_id}")
    return r.json()


def _upstream_sync_enrollment(upstream, external_id, class_inst):
    if class_inst is None:
        class_inst = m.ClassInstance.objects.get(external_id=upstream['class_instance_id'])
    invalid = not all(
        k in upstream
        for k in ('id', 'student', 'class_instance', 'attempt', 'student_year', 'statutes',
                  'attendance', 'attendance_date', 'improvement_grade', 'improvement_grade_date',
                  'continuous_grade', 'continuous_grade_date', 'recourse_grade', 'recourse_grade_date',
                  'special_grade', 'special_grade_date', 'approved'))
    student = m.Student.objects.get(external_id=upstream['student'])

    if (student_year := upstream['student_year']) is not None:
        if student.year is None or student_year > student.year:
            logger.info(f"Updated student {student} year ({student.year} to {student_year})")
            student.year = student_year
            student.save(update_fields=['year'])

    grade = 0
    attendance = upstream['attendance']
    attendance_date = upstream['attendance_date']
    if attendance_date:
        make_aware(datetime.fromisoformat(attendance_date), is_dst=True)

    normal_grade = upstream['continuous_grade']
    if normal_grade:
        grade = normal_grade
    normal_grade_date = upstream['continuous_grade_date']
    if normal_grade_date:
        make_aware(datetime.fromisoformat(normal_grade_date), is_dst=True)
    recourse_grade = upstream['exam_grade']
    if recourse_grade:
        grade = max(grade, recourse_grade)
    recourse_grade_date = upstream['exam_grade_date']
    if recourse_grade_date:
        make_aware(datetime.fromisoformat(recourse_grade_date), is_dst=True)
    special_grade = upstream['special_grade']
    if special_grade:
        grade = max(grade, special_grade)
    special_grade_date = upstream['special_grade_date']
    if special_grade_date:
        make_aware(datetime.fromisoformat(special_grade_date), is_dst=True)

    approved = grade >= 10
    if approved != upstream['approved']:
        logger.debug(f'Upstream enrollment approval does not match the calculated one (enrollment {external_id}).')

    try:
        obj = m.Enrollment.objects.get(external_id=external_id)
        changed = False
        for attr in ('normal_grade_date', 'recourse_grade_date', 'special_grade_date', 'attendance', 'approved'):
            current = getattr(obj, attr)
            new = locals()[attr]
            if current != new:
                setattr(obj, attr, new)
                changed = True
        for attr in ('normal_grade', 'recourse_grade', 'special_grade', 'grade'):
            current = getattr(obj, attr)
            new = locals()[attr]
            if current != new:
                logger.warning(f"Grade changed from {current} to {new} in {obj}.")
                setattr(obj, attr, new)
                changed = True
        if changed:
            obj.save()

    except m.Enrollment.DoesNotExist:
        m.Enrollment.objects.create(
            student=student,
            class_instance=class_inst,
            attendance=attendance,
            attendance_date=attendance_date,
            normal_grade=normal_grade,
            normal_grade_date=normal_grade_date,
            recourse_grade=recourse_grade,
            recourse_grade_date=recourse_grade_date,
            special_grade=special_grade,
            special_grade_date=special_grade_date,
            approved=approved,
            grade=grade,
            external_id=external_id,
            frozen=False,
            external_update=make_aware(datetime.now()))
        logger.info(f"Inserted new enrollment {obj}")


def sync_shift(external_id, class_inst=None, recurse=False):
    """
    Sync the information in a shift
    :param external_id: The foreign id of the shift that is being sync'd
    :param class_inst: The class instance (optional)
    :param recurse: Whether to recurse to the derivative shift instances
    :return:
    """
    upstream = _request_shift_info(external_id)
    _upstream_sync_shift_info(upstream, external_id, class_inst, recurse)


def _request_shift_info(external_id):
    r = requests.get(f"http://{CLIPY['host']}/shift/{external_id}")
    if r.status_code != 200:
        raise Exception(f"Unable to fetch shift {external_id}")
    return r.json()


def _upstream_sync_shift_info(upstream, external_id, class_inst, recurse):
    invalid = not all(
        k in upstream
        for k in ('type', 'number', 'class_instance_id', 'restrictions', 'state', 'instances', 'students', 'teachers'))
    if invalid:
        logger.error(f"Invalid upstream shift instance data: {upstream}")
        return

    if class_inst.external_id != upstream['class_instance_id']:
        logger.critical("Consistency error. Shift upstream parent is not the local parent")
        return

    type_abbr = upstream['type'].upper() if 'type' in upstream else None
    shift_type = None
    for i, abbr in ctypes.ShiftType.ABBREVIATIONS.items():
        if type_abbr == abbr:
            shift_type = i
            break
    if shift_type is None:
        logger.error("Unknown shift type: %s" % type_abbr)
        return

    upstream_details = {'state': upstream['state'], 'restrictions': upstream['restrictions']}
    try:
        obj = m.Shift.objects.get(class_instance=class_inst, external_id=external_id)
        if not obj.frozen and obj.external_data != upstream_details:
            obj.external_data = upstream_details
            obj.save()
    except ObjectDoesNotExist:
        obj = m.Shift.objects.create(
            class_instance=class_inst,
            shift_type=shift_type,
            number=upstream['number'],
            external_id=external_id,
            frozen=False,
            external_update=make_aware(datetime.now()),
            external_data=upstream_details)
        logger.info(f"Shift {obj} created in {class_inst}")

    # ---------  Related shift instances ---------
    instances = obj.instances.exclude(external_id=None).all()

    new, disappeared, mirrored = _upstream_diff(set(instances), set(upstream['instances']))

    if m.ShiftInstance.objects.filter(external_id__in=new).exists():
        logger.critical(f"Some instances of shift {obj} belong to another shift: {new}")
        return

    if recurse:
        for ext_id in new:
            sync_shift_instance(ext_id, shift=obj)

    m.ShiftInstance.objects.filter(external_id__in=mirrored). \
        update(disappeared=False, external_update=make_aware(datetime.now()))
    m.ShiftInstance.objects.filter(external_id__in=disappeared).update(disappeared=True)
    disappeared = m.ShiftInstance.objects.filter(external_id__in=disappeared)
    for instances in disappeared.all():
        logger.warning(f"{instances} removed from {obj}.")

    # ---------  Related M2M ---------
    current_students = m.Student.objects.filter(shift=obj).exclude(disappeared=True)
    new, disappeared, _ = _upstream_diff(current_students, set(upstream['students']))
    m.ShiftStudents.objects.filter(shift=obj, student__external_id__in=disappeared).delete()
    m.ShiftStudents.objects.bulk_create(
        map(lambda student_id: m.ShiftStudents(student_id=student_id, shift=obj),
            m.Student.objects.filter(external_id__in=new).values_list('id', flat=True)))

    current_teachers = m.Teacher.objects.filter(shifts=obj)
    new, disappeared, _ = _upstream_diff(current_teachers, set(upstream['teachers']))
    m.Shift.teachers.through.objects.filter(shift=obj, teacher__external_id__in=disappeared).delete()
    m.Shift.teachers.through.objects.bulk_create(
        map(lambda student_id: m.Shift.teachers.through(teacher_id=student_id, shift=obj),
            m.Teacher.objects.filter(external_id__in=new).values_list('id', flat=True)))


def _upstream_sync_event(upstream, external_id, class_inst):
    invalid = not all(
        k in upstream
        for k in ('id', 'instance_id', 'date', 'from_time', 'to_time', 'type', 'season', 'info', 'note'))

    if invalid:
        logger.error(f"Invalid upstream event data: {upstream}")
        return

    date = make_aware(datetime.fromisoformat(upstream['date']), is_dst=True)
    duration = None

    to_time = upstream['to_time']
    if to_time is not None:
        to_time = datetime.strptime(to_time, "%H:%M")

    from_time = upstream['from_time']
    if from_time is not None:
        if to_time is None:
            logger.error(f"Consistency error syncing event id {external_id}. End time is set but start is not.")
            return
        from_time = datetime.strptime(from_time, "%H:%M")
        duration = (to_time - from_time).seconds // 60
        from_time = from_time.time() # Was a datetime

    if (upstream_info := upstream['info']) is not None:
        info = upstream_info + '.'
        if (upstream_note := upstream['note']) is not None:
            info = f'{info} {upstream_note}'
    else:
        info = None

    try:
        class_event = m.ClassInstanceEvent.objects.get(external_id=external_id)
        changed = False
        if from_time is not None and (class_event.time is None or class_event.time != from_time):
            logger.info(f"Event {class_event} time changed")
            class_event.time = from_time
            if to_time is not None:
                class_event.duration = duration
            # TODO notify users
            changed = True

        if class_event.info != info:
            logger.info(f"Event {class_event} info changed to {info}")
            class_event.info = info
            changed = True

        if class_event.type != upstream['type']:
            logger.info(f"Event {class_event} type changed")
            class_event.type = upstream['type']
            changed = True

        if class_event.type != upstream['season']:
            logger.info(f"Event {class_event} season changed")
            class_event.type = upstream['season']
            changed = True

        if changed:
            class_event.save()

    except m.ClassInstanceEvent.DoesNotExist:
        obj = m.ClassInstanceEvent.objects.create(
            class_instance=class_inst,
            duration=duration,
            date=date,
            time=from_time,
            type=upstream['type'],
            season=upstream['season'],
            info=info,
            external_id=external_id,
            frozen=False,
            external_update=make_aware(datetime.now()))
        logger.info(f"Inserted new class event {obj}")


def sync_shift_instance(external_id, shift):
    """
    Sync the file information in an instance of a shift
    :param external_id: The foreign id of the shift instance that is being sync'd
    :param shift: The parent shift (optional)
    """
    upstream = _request_shift_instance(external_id)
    if upstream is None:
        logger.warning(f"Failed to sync shift instance {external_id} in shift {shift}")
        return
    _upstream_sync_shift_instance(upstream, external_id, shift)


def _request_shift_instance(external_id):
    r = requests.get(f"http://{CLIPY['host']}/shift_inst/{external_id}")
    if r.status_code != 200:
        raise Exception(f"Unable to fetch shift instance {external_id}")
    return r.json()


def _upstream_sync_shift_instance(upstream, external_id, shift):
    if not all(k in upstream for k in ('shift', 'start', 'end', 'weekday', 'room')):
        logger.error(f"Invalid upstream shift instance data: {upstream}")
        return

    if shift.external_id != upstream['shift']:
        logger.critical("Consistency error. ShiftInstance upstream parent is not the local parent")
        return

    upstream_room = None
    if upstream['room'] is not None:
        try:
            upstream_room = m.Room.objects.get(external_id=upstream['room'])
        except m.Room.DoesNotExist:
            logger.warning(f"Room {upstream['room']} is missing (shift instance {external_id})")

    upstream_start = upstream['start']
    upstream_end = upstream['end']
    upstream_weekday = upstream['weekday']
    if not ((isinstance(upstream_start, int) or upstream_start is None)
            and (isinstance(upstream_end, int) or upstream_end is None)
            and (isinstance(upstream_weekday, int) or upstream_weekday is None)):
        logger.error(f"Invalid upstream shift instance data: {upstream}")
        return

    upstream_duration = upstream_end - upstream_start \
        if upstream_end is not None and upstream_start is not None \
        else None

    try:
        shift_instance = m.ShiftInstance.objects.get(shift=shift, external_id=external_id)
        changed = False
        if upstream_start != shift_instance.start:
            logger.warning(f"Shift instance {shift_instance} start changed "
                           f"from {shift_instance.start} to {upstream_start}")
            shift_instance.start = upstream_start
            changed = True

        if upstream_duration != shift_instance.duration:
            if shift_instance.duration is not None:
                logger.warning(f"Shift instance {shift_instance} duration changed "
                               f"from {shift_instance.duration} to {upstream_duration}")
            shift_instance.duration = upstream_duration
            changed = True

        if upstream_weekday != shift_instance.weekday:
            logger.warning(f"Shift instance {shift_instance} weekday changed "
                           f"from {shift_instance.weekday} to {upstream_weekday}")
            shift_instance.weekday = upstream_weekday
            changed = True

        if upstream_room is None:
            if shift_instance.room is not None:
                logger.warning(f"Shift instance {shift_instance} is no longer in a room (was in {shift_instance.room})")
                shift_instance.room = None
                changed = True
        else:
            if shift_instance.room is None:
                shift_instance.room = upstream_room
                changed = True
            elif shift_instance.room != upstream_room:
                logger.warning(f"Shift instance {shift_instance} room changed "
                               f"from {shift_instance.room.external_id} to {upstream['room']}")
                shift_instance.room = upstream_room
                changed = True
        if changed:
            shift_instance.save()
    except m.ShiftInstance.DoesNotExist:
        shift_instance = m.ShiftInstance.objects.create(
            shift=shift,
            weekday=upstream_weekday,
            start=upstream_start,
            duration=upstream_duration,
            room=upstream_room,
            external_id=external_id,
            frozen=False,
            external_update=make_aware(datetime.now()))
        logger.info(f"Shift instance {shift_instance} created.")


def sync_evaluation(external_id, class_inst=None):
    upstream = _request_evaluation(external_id)
    _upstream_sync_evaluation(upstream, external_id, class_inst)


def _request_evaluation(external_id):
    return ''  # TODO Pending crawler implementation


def _upstream_sync_evaluation(upstream, external_id, class_inst):
    pass  # TODO Pending crawler implementation


def sync_students():
    """
    Synchronizes students to the current upstream
    """
    upstream = _request_students()
    _upstream_sync_students(upstream)


def _request_students():
    r = requests.get("http://%s/students/" % CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch students")
    return r.json()


def _upstream_sync_students(upstream_list):
    existing = {student.external_id: student for student in m.Student.objects.exclude(external_id=None).all()}

    for upstream in upstream_list:
        upstream_course = None
        if upstream_course_id := upstream['course']:
            try:
                upstream_course = m.Course.objects.get(external_id=upstream_course_id)
            except m.Course.DoesNotExist:
                logger.error(f'Course {upstream_course} does not exist')

        if (ext_id := upstream['id']) in existing:
            obj = existing[ext_id]
            changed = False
            if (upstream_abbr := upstream['abbr']) is not None:
                if obj.abbreviation != upstream_abbr:
                    logger.warning(f'Student {obj} abbreviation changed ("{obj.abbreviation}" to "{upstream_abbr}").')
                obj.abbreviation = upstream_abbr
                changed = True
            if upstream_course:
                if not obj.course or obj.course != upstream_course:
                    obj.course = upstream_course
                    changed = True
            if (upstream_name := upstream['name']) is not None:
                if obj.external_data is None:
                    obj.external_data = {'name': upstream_name}
                    changed = True
                else:
                    if 'name' in obj.external_data and obj.external_data['name'] != upstream_name:
                        logger.warning(
                            f"Student {obj} name changed from {obj.external_data['name']} to {upstream_name}")
                    obj.external_data['name'] = upstream_name
                    changed = True

            if changed:
                obj.save()
            continue
        else:
            obj = m.Student.objects.create(
                abbreviation=upstream['abbr'],
                iid=upstream['id'],
                number=upstream['id'],
                course=upstream_course,
                external_id=upstream['id'],
                external_update=make_aware(datetime.now()),
                external_data={'name': upstream['name']})
            logger.info(f'Created student {obj}.')


def sync_teachers():
    """
    Synchronizes teachers to the current upstream
    """
    # TODO this method is essentially a duplication of sync_students. Figure a way to generify both
    upstream = _request_teachers()
    _upstream_sync_teachers(upstream)


def _request_teachers():
    r = requests.get("http://%s/teachers/" % CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch teachers")
    return r.json()


def _upstream_sync_teachers(upstream_list):
    existing = {teacher.external_id: teacher for teacher in m.Teacher.objects.exclude(external_id=None).all()}
    departments = {
        department.external_id: department
        for department in m.Department.objects.exclude(external_id=None).all()}

    for upstream in upstream_list:
        upstream_dept_ids = set(upstream['depts'])
        # Does not belong to any known department
        if len(upstream_dept_ids.intersection(departments)) == 0:
            continue
        if (ext_id := upstream['id']) in existing:
            obj = existing[ext_id]
            if (upstream_name := upstream['name']) is not None:
                if obj.name is None:  # Setting unknown is okay
                    obj.name = upstream_name
                    obj.save()
                elif obj.name != upstream_name:  # Setting unknown is okay
                    logger.error(f"Teacher {obj} name changed from {obj.name} to {upstream_name}")
                    continue
        else:
            obj = m.Teacher.objects.create(
                name=upstream['name'],
                iid=upstream['id'],
                external_id=upstream['id'],
                external_update=make_aware(datetime.now()),
                external_data={'name': upstream['name']})
            logger.info(f'Created teacher {obj}.')

        current_departments = obj.departments.all()
        new, disappeared, _ = _upstream_diff(current_departments, upstream_dept_ids)
        m.Teacher.departments.through.objects.filter(teacher=obj, department__external_id__in=disappeared).delete()
        m.Teacher.departments.through.objects.bulk_create(
            map(lambda department_id: m.Teacher.departments.through(department_id=department_id, teacher=obj),
                m.Department.objects.filter(external_id__in=new).values_list('id', flat=True)))


def calculate_active_classes():
    today = date.today()
    current_year = today.year + today.month % 8
    for klass in m.Class.objects.all():
        first_year = 9999
        last_year = 0
        max_enrollments = 0
        changed = False
        for instance in klass.instances.all():
            if instance.year < first_year:
                first_year = instance.year
                changed = True
            if instance.year > last_year:
                last_year = instance.year
                changed = True
            # enrollments = instance.enrollments.count()
            # if enrollments > max_enrollments:
            #     max_enrollments = enrollments
        if changed:
            klass.extinguished = last_year < current_year - 1  # or max_enrollments < 5  # TODO get rid of magic number
            klass.save()


def _upstream_diff(current_objs, clip_ids):
    """
    Calculates the overlap and differences between current and upstream
    :param current_objs: Objects which inherit the Importable model
    :param clip_ids: External ids that are upstream
    :return: new, old, and mirrored external id's
    """
    current_objects = {obj.external_id: obj for obj in current_objs}
    inserted_ids = {obj.external_id for obj in current_objects.values()}
    current_ids = {obj.external_id for obj in current_objects.values() if not obj.disappeared}
    new = clip_ids.difference(inserted_ids)
    disappeared = current_ids.difference(clip_ids)
    mirrored = inserted_ids.intersection(clip_ids)
    return new, disappeared, mirrored


def _related(children, clip_children_ids, related_func, related_type, recurse, **recurse_kwargs):
    """
    Aux function to handle the children related info
    :param children: Current children objects
    :param clip_children_ids: Upstream children external ids
    :param related_func: Function that handles every children (if recurse is true)
    :param related_type: Type of the children objects
    :param recurse: Whether to recurse the instantiation (same process for children and so forth)
    :param recurse_kwargs: Args to pass to the related_func
    """
    new, disappeared, mirrored = _upstream_diff(set(children), set(clip_children_ids))

    if recurse:
        [related_func(ext_id, recurse=True, **recurse_kwargs) for ext_id in new]

    disappeared = related_type.objects.filter(external_id__in=disappeared)
    for disappeared_obj in disappeared.all():
        logger.warning(f"{disappeared_obj} disappeared.")
    related_type.objects.filter(external_id__in=mirrored).update(external_update=make_aware(datetime.now()))


def _closest_teacher(teachers, name):
    """
    Finds the teacher in a dict {name: teacher} whose the name is the closest to the provided parameter
    :param teachers: Teacher dict
    :param name: Name to find
    :return: Closest match
    """
    uploader_teacher = None
    max_correlation = 0
    for teacher_name, teacher in teachers.items():
        c = correlation(name, teacher_name)
        if c > max_correlation:
            uploader_teacher = teacher
            max_correlation = c
    return uploader_teacher
