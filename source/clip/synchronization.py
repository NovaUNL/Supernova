import re
from datetime import date, datetime
import requests
import logging
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


def rooms():
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
        if clip_department['institution'] != CLIPY['institution']:
            continue
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
    for class_ in disappeared.all():
        logger.warning(f"{class_} removed from {department}.")

    # ---------  Related teachers ---------
    # Handled in the teacher method


def sync_class(external_id, department=None, recurse=False):
    """
    Sync the information in a class
    :param external_id: The foreign id of the class that is being sync'd
    :param department: The parent department of this class (optional)
    :param recurse: Whether to recurse to the derivative entities (class instances)
    """
    upstream = _request_class(external_id)
    _upstream_sync_class(upstream, external_id, department, recurse)


def _request_class(external_id):
    r = requests.get(f"http://{CLIPY['host']}/class/{external_id}")
    if r.status_code != 200:
        raise Exception("Unable to fetch class")
    return r.json()


def _upstream_sync_class(upstream, external_id, department, recurse):
    if department is None:
        department = m.Department.objects.get(external_id=upstream['dept'])

    try:
        obj = m.Class.objects.get(department=department, external_id=external_id)
    except ObjectDoesNotExist:
        obj = m.Class.objects.create(
            name=upstream['name'],
            abbreviation=upstream['abbr'],
            department=department,
            credits=upstream['ects'],
            iid=upstream['iid'],
            external_id=external_id,
            frozen=False,
            external_update=make_aware(datetime.now()))
        logger.info(f"Created class {obj}")

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
        if (dept_ext_id := upstream['dept']) != obj.department.external_id:
            new_department = m.Department.objects.filter(external_id=dept_ext_id).first()
            if new_department is None:
                logger.error(f"Class {obj} department changed from {obj.department} "
                             f"to an unknown department (id:{dept_ext_id}). Ignoring.")
            else:
                logger.warning(f"Class {obj} department changed from {obj.department} to {new_department}")
                obj.department = new_department
                changed = True
        if changed:
            obj.save()

    # ---------  Related Instances ---------
    instances = obj.instances.exclude(external_id=None).all()

    new, disappeared, mirrored = _upstream_diff(set(instances), set(upstream['instances']))

    # Class instances do not simply move to another class
    if m.ClassInstance.objects.filter(external_id__in=new).exists():
        logger.critical(f"Some instances of class {obj} belong to another class: {new}")

    if recurse:
        for ext_id in new:
            sync_class_instance(ext_id, recurse=True, class_=obj)

    m.ClassInstance.objects.filter(external_id__in=mirrored). \
        update(disappeared=False, external_update=make_aware(datetime.now()))
    m.ClassInstance.objects.filter(external_id__in=disappeared).update(disappeared=True)
    disappeared = m.ClassInstance.objects.filter(external_id__in=disappeared)
    for instance in disappeared.all():
        logger.warning(f"{instance} removed from {obj}.")


def sync_class_instance(external_id, class_=None, recurse=False):
    """
    Sync the information in a class instance
    :param external_id: The foreign id of the class instance that is being sync'd
    :param class_: The class that is parent this class instance (optional)
    :param recurse: Whether to recurse to the derivative entities (turns, enrollments and evaluations)
    """
    upstream = _request_class_instance(external_id)
    _upstream_sync_class_instance(upstream, external_id, class_, recurse)


def _request_class_instance(external_id):
    r = requests.get(f"http://{CLIPY['host']}/class_inst/{external_id}")
    if r.status_code != 200:
        raise Exception(f"Unable to fetch class instance {external_id}")
    return r.json()


def _upstream_sync_class_instance(upstream, external_id, class_, recurse):
    if class_ is None:
        class_ = m.Class.objects.get(external_id=upstream['class_id'])

    try:
        obj = m.ClassInstance.objects.get(parent=class_, external_id=external_id)
    except ObjectDoesNotExist:
        obj = m.ClassInstance.objects.create(
            parent=class_,
            year=upstream['year'],
            period=upstream['period'],
            external_id=external_id,
            information=upstream['info'],
            frozen=False,
            external_update=make_aware(datetime.now()))
        logger.info(f"Class instance {obj} created")

    if not obj.frozen:
        changed = False
        if upstream['year'] != obj.year:
            logger.error(f"Instance {obj} year remotely changed from {obj.year} to {upstream['year']}")
            obj.year = upstream['year']
            changed = True

        if upstream['period'] != obj.period:
            logger.error(f"Instance {obj} period remotely changed from {obj.period} to {upstream['period']}")
            obj.period = upstream['period']
            changed = True

        if changed:
            obj.save()

    # TODO sync other info

    # ---------  Related ---------
    turns = obj.turns.exclude(external_id=None).all()
    _related(turns, upstream['turns'], sync_turn, m.Turn, recurse, class_inst=obj)
    enrollments = obj.enrollments.exclude(external_id=None).all()
    _related(enrollments, upstream['enrollments'], sync_enrollment, m.Enrollment, recurse, class_inst=obj)
    _related(turns, upstream['turns'], sync_turn, m.Turn, recurse, class_inst=obj)

    sync_class_instance_files(external_id, class_inst=obj)  # Must happen after the turn sync to have the teachers known
    # TODO
    # evaluations = obj.enrollments.exclude(external_id=None).all()
    # _related(evaluations, upstream['evaluations'], sync_evaluation, m.ClassEvaluation, recurse, class_inst=obj)


def sync_class_instance_files(external_id, class_inst=None):
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
    teachers = {teacher.name: teacher for teacher in m.Teacher.objects.filter(turns__class_instance=class_inst).all()}

    for hash in mirrored:
        upsteam_info = upstream[hash]
        downstream_file: m.ClassFile = downstream_files[hash]
        changed = False
        if downstream_file.name != (name := upsteam_info['name']):
            logger.warning(f"{downstream_file} name changed to {name}")
            downstream_file.name = name
            changed = True
        upstream_date = make_aware(datetime.fromisoformat(upsteam_info['upload_datetime']))
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
                upload_datetime=make_aware(datetime.fromisoformat(upsteam_info['upload_datetime'])),
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
    _upstream_sync_enrollment(upstream, external_id, class_inst)


def _request_enrollment(external_id):
    r = requests.get(f"http://{CLIPY['host']}/enrollment/{external_id}")
    if r.status_code != 200:
        raise Exception(f"Unable to fetch enrollment {external_id}")
    return r.json()


def _upstream_sync_enrollment(upstream, external_id, class_inst):
    if class_inst is None:
        class_inst = m.ClassInstance.objects.get(external_id=upstream['class_instance_id'])

    try:
        obj = m.Enrollment.objects.get(class_instance=class_inst, external_id=external_id)
    except ObjectDoesNotExist:
        obj = m.Enrollment.objects.create(
            student=m.Student.objects.get(external_id=upstream['student']),
            class_instance=class_inst,
            external_id=external_id,
            frozen=False,
            external_update=make_aware(datetime.now()))


def sync_turn(external_id, class_inst=None, recurse=False):
    """
    Sync the information in a turn
    :param external_id: The foreign id of the turn that is being sync'd
    :param class_inst: The class instance (optional)
    :param recurse: Whether to recurse to the derivative turn instances
    :return:
    """
    upstream = _request_turn_info(external_id)
    _upstream_sync_turn_info(upstream, external_id, class_inst, recurse)


def _request_turn_info(external_id):
    r = requests.get(f"http://{CLIPY['host']}/turn/{external_id}")
    if r.status_code != 200:
        raise Exception(f"Unable to fetch turn {external_id}")
    return r.json()


def _upstream_sync_turn_info(upstream, external_id, class_inst, recurse):
    if class_inst is None:
        class_inst = m.ClassInstance.objects.get(external_id=upstream['class_instance_id'])

    type_abbr = upstream['type'].upper() if 'type' in upstream else None
    turn_type = None
    for i, abbr in ctypes.TurnType.ABBREVIATIONS.items():
        if type_abbr == abbr:
            turn_type = i
            break
    try:
        obj = m.Turn.objects.get(class_instance=class_inst, external_id=external_id)
    except ObjectDoesNotExist:
        obj = m.Turn.objects.create(
            class_instance=class_inst,
            turn_type=turn_type,
            number=upstream['number'],
            external_id=external_id,
            frozen=False,
            external_update=make_aware(datetime.now()))
        logger.info(f"Turn {obj} created in {class_inst}")

    # ---------  Related ---------
    turn_instances = obj.instances.exclude(external_id=None).all()
    _related(turn_instances, upstream['instances'], sync_turn_instance, m.Turn, recurse, turn=obj)
    # ---------  Related M2M ---------
    current_students = m.Student.objects.filter(turn=obj).exclude(disappeared=True)
    new, disappeared, _ = _upstream_diff(current_students, set(upstream['students']))
    m.TurnStudents.objects.filter(turn=obj, student__external_id__in=disappeared).delete()
    m.TurnStudents.objects.bulk_create(
        map(lambda student_id: m.TurnStudents(student_id=student_id, turn=obj),
            m.Student.objects.filter(external_id__in=new).values_list('id', flat=True)))

    current_teachers = m.Teacher.objects.filter(turns=obj)
    new, disappeared, _ = _upstream_diff(current_teachers, set(upstream['teachers']))
    m.Turn.teachers.through.objects.filter(turn=obj, teacher__external_id__in=disappeared).delete()
    m.Turn.teachers.through.objects.bulk_create(
        map(lambda student_id: m.Turn.teachers.through(teacher_id=student_id, turn=obj),
            m.Teacher.objects.filter(external_id__in=new).values_list('id', flat=True)))


def sync_turn_instance(external_id, turn=None):
    """
    Sync the file information in an instance of a turn
    :param external_id: The foreign id of the turn instance that is being sync'd
    :param turn: The parent turn (optional)
    """
    upstream = _request_turn_instance(external_id)
    _upstream_sync_turn_instance(upstream, external_id, turn)


def _request_turn_instance(external_id):
    r = requests.get(f"http://{CLIPY['host']}/turn_inst/{external_id}")
    if r.status_code != 200:
        raise Exception(f"Unable to fetch turn instance {external_id}")
    return r.json()


def _upstream_sync_turn_instance(upstream, external_id, turn):
    if turn is None:
        turn = m.Turn.objects.get(external_id=upstream['turn'])

    try:
        obj = m.TurnInstance.objects.get(turn=turn, external_id=external_id)
    except ObjectDoesNotExist:
        obj = m.TurnInstance.objects.create(
            turn=turn,
            weekday=upstream['weekday'],
            start=upstream['start'],
            duration=upstream['end'] - upstream['start'],
            room=m.Room.objects.get(external_id=upstream['room']),
            external_id=external_id,
            frozen=False,
            external_update=make_aware(datetime.now()))
        logger.info(f"Turn instance {obj} created.")

    if upstream['start'] != obj.start:
        logger.warning(f"Turn instance {obj} start changed from {obj.start} to {upstream['start']}")
    if upstream['end'] != obj.start + obj.duration:
        logger.warning(
            f"Turn instance {obj} duration changed from {obj.duration} to {upstream['end'] - upstream['start']}")
    if upstream['weekday'] != obj.weekday:
        logger.warning(f"Turn instance {obj} weekday changed from {obj.weekday} to {upstream['weekday']}")
    if upstream['room'] != obj.room.external_id:
        logger.warning(f"Turn instance {obj} room changed from {obj.room.external_id} to {upstream['room']}")


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
        if upstream['inst'] != CLIPY['institution']:
            continue
        if (ext_id := upstream['id']) in existing:
            obj = existing[ext_id]
            changed = False
            if (upstream_iid := upstream['iid']) is not None:
                if obj.iid is None:  # Setting unknown is okay
                    obj.iid = upstream_iid
                    changed = True
                elif obj.iid != str(upstream_iid):  # Changing known is not
                    logger.error(f"Student {obj} IID changed from {obj.iid} to {upstream_iid}")
            if (upstream_abbr := upstream['abbr']) is not None:
                if obj.abbreviation is None:  # Setting unknown is okay
                    obj.abbreviation = upstream_abbr
                    changed = True
                elif obj.abbreviation != upstream_abbr:  # Changing known is not
                    logger.error(f"Student {obj} abbreviation changed from {obj.abbreviation} to {upstream_abbr}")
            if (upstream_name := upstream['name']) is not None:
                if obj.external_data is None:
                    obj.external_data = {'name': upstream_name}
                    changed = True
                elif 'name' in obj.external_data:
                    if obj.external_data['name'] != upstream_name:
                        logger.error(f"Student {obj} name changed from {obj.name} to {upstream_name}")
                else:
                    obj.external_data['name'] = upstream_name
                    changed = True

            if changed:
                obj.save()
            continue
        else:
            obj = m.Student.objects.create(
                abbreviation=upstream['abbr'],
                iid=upstream['iid'],
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
    for class_ in m.Class.objects.all():
        first_year = 9999
        last_year = 0
        max_enrollments = 0
        for instance in class_.instances.all():
            if instance.year < first_year:
                first_year = instance.year
            if instance.year > last_year:
                last_year = instance.year
            # enrollments = instance.enrollments.count()
            # if enrollments > max_enrollments:
            #     max_enrollments = enrollments

        class_.extinguished = last_year < current_year - 2  # or max_enrollments < 5  # TODO get rid of magic number
        class_.save()


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
