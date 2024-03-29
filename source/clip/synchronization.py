import re
from datetime import date, datetime
from functools import reduce
from itertools import chain
import logging

from django.db import IntegrityError
from django.db.models import Q, Max, Sum
from django.utils import timezone
from django.utils.timezone import make_aware
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

import requests
import reversion

from college import models as m, choice_types as ctypes
from supernova.utils import correlation

logger = logging.getLogger(__name__)


class NetworkException(Exception):
    pass


class Recursivity:
    NONE = 0
    CREATION = 1
    FULL = 2


# TODO deduplicate code in _request methods
# TODO deduplicate code in relationships

def assert_buildings_inserted():
    ignored = {2, 1191, 1197, 1198, 1632, 1653}
    whitelisted = {
        1176, 1177, 1178, 1179, 1180, 1181, 1183, 1184, 1185,
        1186, 1188, 1189, 1190, 1238, 1395, 1561, 1564, 1663}
    r = requests.get("http://%s/buildings/" % settings.CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch buildings")
    clip_buildings = r.json()
    ids = set(map(lambda item: item['id'], clip_buildings))
    missing = ids.difference(set(m.Building.objects.values_list('external_id', flat=True)))
    missing = missing.difference(ignored)
    for building in clip_buildings:
        if building['id'] in missing:
            if building['id'] in whitelisted:
                with reversion.create_revision():
                    m.Building.objects.create(
                        name=building['name'],
                        iid=building['id'],
                        external_id=building['id'],
                        abbreviation=building['name'][:15],
                        map_tag=building['name'][:15],
                        frozen=False,
                        external_update=make_aware(datetime.now()),
                        external_data={'upstream': building})
            else:
                logger.info(f'Building {building} missing.')


door_number_exp = re.compile('(?P<floor>\d)\.?(?P<door_number>\d+)')


def sync_rooms():
    """
    Fetches the most recent available info about rooms.
    Creates missing rooms.
    """
    r = requests.get("http://%s/rooms/" % settings.CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch rooms")

    existing = {room.external_id: room for room in m.Room.objects.all()}
    for clip_room in r.json():
        try:
            building = m.Building.objects.get(external_id=clip_room['building'])
        except ObjectDoesNotExist:
            logger.warning(f"Skipped room {clip_room} (building not found)")
            continue

        room = existing.get(clip_room['id'])

        if room is None:  # New room
            with reversion.create_revision():
                room = m.Room.objects.create(
                    name=clip_room['name'],
                    type=clip_room["type"],
                    building=building,
                    external_id=clip_room['id'],
                    iid=clip_room['id'],
                    frozen=False,
                    external_update=make_aware(datetime.now()))
                logger.info(f'Created room {room}.')
            continue

        logger.debug(f'Room {room} already exists.')
        if not room.frozen:
            changed = False
            with reversion.create_revision():
                if room.building != building:
                    logger.warning(f'Building for room {room} changed to building {building}.')
                    room.building = building
                    changed = True

                if room.name != clip_room["name"]:
                    logger.warning(f'Room {room} changed name to {clip_room["name"]}.')
                    room.name = clip_room["name"]
                    changed = True

                if room.type != clip_room["type"]:
                    logger.warning(f'Room {room} type changed to {clip_room["type"]}.')
                    # room.type = clip_room["type"] TODO uncomment after freezing manually changed rooms
                    # changed = True
                door_matches = door_number_exp.search(clip_room['name'])
                if door_matches:
                    floor = int(door_matches.group('floor'))
                    if room.floor != floor:
                        room.floor = floor
                        changed = True
                    door_number = int(door_matches.group('door_number'))
                    if room.door_number != door_number:
                        room.door_number = door_number
                        changed = True
                if changed:
                    room.save()
            room.external_update = make_aware(datetime.now())
            room.save(update_fields=['external_update'])


def sync_courses():
    """
    Fetches the most recent available info about courses.
    Creates missing courses.
    """
    r = requests.get("http://%s/courses/" % settings.CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch courses")

    existing = {course.external_id: course for course in m.Course.objects.all()}
    for upstream_course in r.json():
        course = existing.get(upstream_course['id'])

        if course is None:  # New course
            if upstream_course['deg'] is None:
                logger.debug(f'Course {upstream_course["name"]} ignored due to null degree.')
                continue
            with reversion.create_revision():
                course = m.Course.objects.create(
                    name=upstream_course['name'],
                    degree=upstream_course['deg'],
                    abbreviation=upstream_course["abbr"],
                    external_id=upstream_course['id'],
                    iid=upstream_course['id'],
                    frozen=False,
                    external_update=make_aware(datetime.now()))
                logger.info(f'Created course {course}.')
            continue

        logger.debug(f'Course {course} already exists.')
        changed = False
        if not course.frozen:
            with reversion.create_revision():
                if course.name != upstream_course["name"]:
                    logger.warning(f'Course {course} changed name to {upstream_course["name"]}.')
                    course.name = upstream_course["name"]
                    changed = True
                if course.degree != upstream_course["deg"]:
                    logger.warning(f'Course {course} changed degree to {upstream_course["deg"]}.')
                    course.degree = upstream_course["deg"]
                    changed = True
                if course.abbreviation != upstream_course["abbr"]:
                    logger.warning(f'Course {course} changed abbreviation to {upstream_course["abbr"]}.')
                    course.abbreviation = upstream_course["abbr"]
                    changed = True
                if changed:
                    course.save()

            course.external_update = make_aware(datetime.now())
            course.save(update_fields=['external_update'])


def sync_departments():
    upstream = _request_departments()
    _upstream_sync_departments(upstream)


def _request_departments():
    r = requests.get("http://%s/departments/" % settings.CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch departments")
    return r.json()


def _upstream_sync_departments(upstream):
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
            with reversion.create_revision():
                department = m.Department.objects.create(
                    name=clip_department['name'],
                    iid=clip_department['id'],
                    external_id=clip_department['id'],
                    frozen=False,
                    external_update=make_aware(datetime.now()),
                    external_data={'upstream': upstream})
                logger.info(f'Created department {department}.')


def sync_department(department, recurse=Recursivity.NONE):
    """
    Sync the information in a department
    :param department: The department that is being sync'd
    :param recurse: Whether to recurse to the derivative entities (classes)
    """
    upstream = _request_department(department)
    _upstream_sync_department(upstream, department, recurse)


def _request_department(department):
    r = requests.get(f"http://{settings.CLIPY['host']}/department/{department.external_id}")
    if r.status_code != 200:
        raise Exception(f"Unable to fetch department {department.external_id}")
    return r.json()


def _upstream_sync_department(upstream, department, recurse=Recursivity.NONE):
    pass
    # ---------  Related classes ---------
    # TODO DEPRECATED
    # classes = department.classes.exclude(external_id=None).all()
    # new, disappeared, mirrored = _upstream_diff(set(classes), set(upstream['classes']))
    #
    # if recurse:
    #     for ext_id in new:
    #         sync_class(ext_id, recurse=True)
    #
    # m.Class.objects.filter(external_id__in=new).update(department=department)
    # m.Class.objects.filter(external_id__in=mirrored).update(external_update=make_aware(datetime.now()))
    # m.Class.objects.filter(external_id__in=disappeared).update(department=None)
    # disappeared = m.Class.objects.filter(external_id__in=disappeared)
    # for klass in disappeared.all():
    #     logger.warning(f"{klass} removed from {department}.")

    # ---------  Related teachers ---------
    # Handled in the teacher function


def sync_classes(recurse=Recursivity.NONE):
    upstream = _request_classes()
    _upstream_sync_classes(upstream, recurse)


def _request_classes():
    r = requests.get("http://%s/classes/" % settings.CLIPY['host'])
    if r.status_code != 200:
        raise Exception("Unable to fetch classes")
    return r.json()


def _upstream_sync_classes(upstream, recurse):
    known_ids = set(
        m.Class.objects
            .exclude(external_id=None)
            .exclude(disappeared=True)
            .values_list('external_id', flat=True))
    clip_ids = {entry['id'] for entry in upstream}
    disappeared = known_ids.difference(clip_ids)
    mirrored = known_ids.intersection(clip_ids)

    disappeared_classes = m.Class.objects.filter(external_id__in=disappeared)
    for klass in disappeared_classes.all():
        logger.warning(f"Class {klass.name} disappeared")
    disappeared_classes.update(disappeared=True, external_update=make_aware(datetime.now()))
    m.Class.objects \
        .filter(external_id__in=mirrored) \
        .update(external_update=make_aware(datetime.now()), disappeared=False)

    for clip_class in upstream:
        if clip_class['id'] not in disappeared:
            _upstream_sync_class(clip_class, clip_class['id'], recurse)


def sync_class(external_id, recurse=Recursivity.NONE):
    """
    Sync the information in a class
    :param external_id: The foreign id of the class that is being sync'd
    :param recurse: Whether to recurse to the derivative entities (class instances)
    """
    upstream = _request_class(external_id)
    _upstream_sync_class(upstream, external_id, recurse)


def _request_class(external_id):
    r = requests.get(f"http://{settings.CLIPY['host']}/class/{external_id}")
    if r.status_code != 200:
        raise Exception("Unable to fetch class")
    return r.json()


def _upstream_sync_class(upstream, external_id, recurse):
    if not all(
            k in upstream
            for k in ('id', 'name', 'abbr', 'ects', 'instances')):
        logger.error(f"Invalid class instance data: {upstream}")
        return

    upstream_id = upstream['id']
    upstream_name = upstream['name']
    upstream_abbr = upstream['abbr']
    upstream_ects = upstream['ects']
    upstream_instances = upstream['instances']

    try:
        obj = m.Class.objects.get(external_id=external_id)
        if not obj.frozen:
            with reversion.create_revision():
                changed = False
                if upstream_name != obj.name:
                    logger.warning(f"Class {obj} name changed from {obj.name} to {upstream_name}")
                    obj.name = upstream_name
                    changed = True
                if upstream_abbr != obj.abbreviation:
                    logger.warning(f"Class {obj} abbreviation changed from {obj.abbreviation} to {upstream_abbr}")
                    obj.abbreviation = upstream_abbr
                    changed = True
                if upstream_ects != obj.credits:
                    logger.warning(f"Class {obj} credits changed from {obj.credits} to {upstream_ects}")
                    obj.credits = upstream_ects
                    changed = True
                if obj.external_data != upstream:
                    obj.external_data = upstream
                    changed = True
                if changed:
                    obj.save()
    except ObjectDoesNotExist:
        with reversion.create_revision():
            obj = m.Class.objects.create(
                name=upstream_name,
                abbreviation=upstream_abbr,
                credits=upstream_ects,
                iid=upstream_id,
                external_id=external_id,
                frozen=False,
                external_update=make_aware(datetime.now()),
                external_data={'upstream': upstream})
            logger.info(f"Created class {obj}")

    # ---------  Related Instances ---------
    instances = obj.instances.exclude(external_id=None).all()

    new, disappeared, mirrored = _upstream_diff(set(instances), set(upstream_instances))

    # Class instances do not simply move to another class
    if m.ClassInstance.objects.filter(external_id__in=new).exists():
        logger.critical(f"Some instances of class {obj} belong to another class: {new}")

    m.ClassInstance.objects.filter(external_id__in=mirrored). \
        update(disappeared=False, external_update=make_aware(datetime.now()))
    m.ClassInstance.objects.filter(external_id__in=disappeared).update(disappeared=True)
    disappeared = m.ClassInstance.objects.filter(external_id__in=disappeared)
    for instance in disappeared.all():
        logger.warning(f"{instance} removed from {obj}.")

    if recurse == Recursivity.CREATION:
        for ext_id in new:
            sync_class_instance(ext_id, recurse=recurse, klass=obj)
    elif recurse == Recursivity.FULL:
        for ext_id in chain(new, mirrored):
            sync_class_instance(ext_id, recurse=recurse, klass=obj)


def sync_class_instance(external_id, klass=None, recurse=Recursivity.NONE):
    """
    Sync the information in a class instance
    :param external_id: The foreign id of the class instance that is being sync'd
    :param klass: The class that is parent this class instance (optional)
    :param recurse: Whether to recurse to the derivative entities (shifts, enrollments and evaluations)
    """
    upstream = _request_class_instance(external_id)
    _upstream_sync_class_instance(upstream, external_id, klass, recurse)


def _request_class_instance(external_id):
    r = requests.get(f"http://{settings.CLIPY['host']}/class_inst/{external_id}")
    if r.status_code != 200:
        raise NetworkException(f"Unable to fetch class instance {external_id}")
    return r.json()


def _upstream_sync_class_instance(upstream, external_id, klass, recurse):
    if not all(
            k in upstream
            for k in ('department_id', 'enrollments', 'events', 'files', 'shifts', 'info', 'period', 'year')):
        logger.error(f"Invalid class instance data: {upstream}")
        return

    upstream_department = upstream['department_id']
    upstream_enrollments = upstream['enrollments']
    upstream_events = upstream['events']
    upstream_files = upstream['files']
    upstream_shifts = upstream['shifts']
    upstream_info = upstream['info']
    upstream_period = upstream['period']
    upstream_year = upstream['year']

    if klass is None:
        klass = m.Class.objects.get(external_id=upstream['class_id'])

    if upstream_department:
        try:
            department = m.Department.objects.get(external_id=upstream['department_id'])
        except m.Department.DoesNotExist:
            department = sync_department(department=upstream_department)
            if department is None:
                logger.error(f"Unable to retrieve department {department} (found in CI {external_id})")

    else:
        department = None

    try:
        obj = m.ClassInstance.objects.get(parent=klass, external_id=external_id)
        if not obj.frozen:
            with reversion.create_revision():
                changed = False
                if upstream_year != obj.year:
                    logger.error(f"Instance {obj} year remotely changed from {obj.year} to {upstream_year}")
                    # obj.year = upstream_year
                    # changed = True

                if upstream_period != obj.period:
                    logger.error(f"Instance {obj} period remotely changed from {obj.period} to {upstream_period}")
                    # obj.period = upstream_period
                    # changed = True

                if obj.information is None:
                    obj.information = {'upstream': upstream_info}
                    changed = True

                if obj.external_data != upstream:
                    obj.external_data = upstream
                    changed = True

                elif 'upstream' not in obj.information or obj.information['upstream'] != upstream_info:
                    obj.information['upstream'] = upstream_info
                    changed = True
                if changed:
                    obj.save()
    except ObjectDoesNotExist:
        with reversion.create_revision():
            try:
                period_inst = m.PeriodInstance.objects.get(year=upstream_year, type=upstream_period)
            except m.PeriodInstance.DoesNotExist:
                period_inst = m.PeriodInstance.objects.create(year=upstream_year, type=upstream_period)
            obj = m.ClassInstance.objects.create(
                parent=klass,
                year=upstream_year,
                period=upstream_period,
                period_instance=period_inst,
                department=department,
                external_id=external_id,
                information={'upstream': upstream_info},
                frozen=False,
                external_update=timezone.now(),
                external_data={'upstream': upstream})
            logger.info(f"Class instance {obj} created")
            if klass.department != department:
                if department is None:
                    logger.warning(f'Attempted to change class {klass} department from {klass.department} to none.')
                else:
                    if klass.instances.order_by('year', 'period').reverse().first() == obj:
                        logger.info(f'Changed class {klass} department from {klass.department} to {department}')
                        klass.department = department
                        klass.save()

    # ---------  Related shifts ---------
    shifts = obj.shifts.exclude(external_id=None).all()
    upstream_shifts = {shift['id']: shift for shift in upstream_shifts}
    new, disappeared, mirrored = _upstream_diff(set(shifts), set(upstream_shifts))

    if m.Shift.objects.filter(external_id__in=new).exists():
        logger.critical(f"Some shifts of class instance {obj} belong to another instance: {new}")

    m.Shift.objects \
        .filter(external_id__in=mirrored). \
        update(disappeared=False, external_update=make_aware(datetime.now()))
    m.Shift.objects.filter(external_id__in=disappeared).update(disappeared=True)
    disappeared = m.Shift.objects.filter(external_id__in=disappeared)
    for shift in disappeared.all():
        logger.warning(f"{shift} removed from {obj}.")

    if recurse == Recursivity.CREATION:
        for ext_id in new:
            upstream_data = upstream_shifts[ext_id]
            _upstream_sync_shift_info(upstream_data, ext_id, recurse=recurse, class_inst=obj)
    elif recurse == Recursivity.FULL:
        for ext_id in chain(new, mirrored):
            upstream_data = upstream_shifts[ext_id]
            _upstream_sync_shift_info(upstream_data, ext_id, recurse=recurse, class_inst=obj)

    # ---------  Related Events ---------
    events = obj.events.exclude(external_id=None).all()
    upstream_events = {event['id']: event for event in upstream_events}
    new, disappeared, mirrored = _upstream_diff(set(events), set(upstream_events.keys()))

    if m.ClassInstanceEvent.objects.filter(external_id__in=new).exists():
        logger.critical(f"Some event of class instance {obj} belongs to another instance: {new}")

    m.ClassInstanceEvent.objects.filter(external_id__in=mirrored). \
        update(disappeared=False, external_update=make_aware(datetime.now()))
    m.ClassInstanceEvent.objects.filter(external_id__in=disappeared).update(disappeared=True)
    disappeared = m.ClassInstanceEvent.objects.filter(external_id__in=disappeared)
    for event in disappeared.all():
        logger.warning(f"{event} removed from {obj}.")

    if recurse == Recursivity.CREATION:
        for ext_id in new:
            upstream_data = upstream_events[ext_id]
            _upstream_sync_event(upstream_data, ext_id, class_inst=obj)
    elif recurse == Recursivity.FULL:
        for ext_id in chain(new, mirrored):
            upstream_data = upstream_events[ext_id]
            _upstream_sync_event(upstream_data, ext_id, class_inst=obj)

    # ---------  Related enrollments ---------
    enrollments = obj.enrollments.exclude(external_id=None).all()
    upstream_enrollments = {enrollment['id']: enrollment for enrollment in upstream_enrollments}
    new, disappeared, mirrored = _upstream_diff(set(enrollments), set(upstream_enrollments))

    if m.Enrollment.objects.filter(external_id__in=new).exists():
        logger.critical(f"Some enrollments of class instance {obj} belong to another instance: {new}")

    m.Enrollment.objects.filter(external_id__in=mirrored). \
        update(disappeared=False, external_update=make_aware(datetime.now()))
    m.Enrollment.objects.filter(external_id__in=disappeared).update(disappeared=True)
    disappeared = m.Enrollment.objects.filter(external_id__in=disappeared)
    for enrollment in disappeared.all():
        logger.warning(f"{enrollment} removed from {obj}.")

    if recurse == Recursivity.CREATION:
        for ext_id in new:
            upstream_data = upstream_enrollments[ext_id]
            _upstream_sync_enrollment(upstream_data, ext_id, class_inst=obj)
    elif recurse == Recursivity.FULL:
        for ext_id in chain(new, mirrored):
            upstream_data = upstream_enrollments[ext_id]
            _upstream_sync_enrollment(upstream_data, ext_id, class_inst=obj)

    # ---------  Related files ---------
    if recurse in (Recursivity.CREATION, Recursivity.FULL):
        _upstream_sync_class_instance_files(upstream_files, external_id, class_inst=obj)


def sync_class_instance_files(external_id, class_inst):
    """
    Sync the file information in a class instance
    :param external_id: The foreign id of the class instance that is being sync'd
    :param class_inst: The class instance
    """
    upstream = _request_class_instance_files(external_id)
    _upstream_sync_class_instance_files(upstream, external_id, class_inst)


def _request_class_instance_files(external_id):
    r = requests.get(f"http://{settings.CLIPY['host']}/files/{external_id}")
    if r.status_code != 200:
        raise NetworkException("Unable to fetch class instance files")
    return r.json()


def _upstream_sync_class_instance_files(upstream, external_id, class_inst):
    invalid = not all(
        k in upstream_entry
        for upstream_entry in upstream
        for k in ('id', 'hash', 'mime', 'name', 'size', 'type', 'upload_datetime', 'uploader'))
    if invalid:
        logger.error(f"Invalid files in class instance id {external_id}: {upstream}")
        return

    if class_inst is None:
        class_inst = m.ClassInstance.objects.prefetch_related('files__file').get(external_id=external_id)

    upstream_count = len(upstream)
    upstream = {
        entry['hash']: entry
        for entry in filter(lambda entry: 'hash' in entry and entry['hash'], upstream)
    }
    downloaded_upstream_count = len(upstream)
    if upstream_missing_count := (upstream_count - downloaded_upstream_count):
        logger.warning(f"Class instance id {external_id} has {upstream_missing_count} undownloaded files")

    upstream_ids = set(upstream.keys())
    downstream_files = {ifile.file.hash: ifile
                        for ifile in class_inst.files.select_related('file').exclude(external_id=None).all()}
    downstream_ids = set(downstream_files.keys())
    new = upstream_ids.difference(downstream_ids)
    removed = downstream_ids.difference(upstream_ids)
    mirrored = downstream_ids.intersection(upstream_ids)
    teachers = {teacher.name: teacher for teacher in m.Teacher.objects.filter(shifts__class_instance=class_inst).all()}

    for hash in mirrored:
        upsteam_info = upstream[hash]
        downstream_file: m.ClassFile = downstream_files[hash]
        if not downstream_file.frozen:
            changed = False
            with reversion.create_revision():
                if downstream_file.disappeared:
                    downstream_file.disappeared = False
                    changed = True

                known_upsteam_name = None
                if downstream_file.external_data and 'upstream' in downstream_file.external_data:
                    known_upsteam_name = downstream_file.external_data['upstream']['name']
                file_name_diverged = downstream_file.name != known_upsteam_name
                if known_upsteam_name != (upstream_name := upsteam_info['name']) \
                        and downstream_file.name != upstream_name:
                    logger.warning(f"{downstream_file} name changed to {upstream_name}")
                    if not file_name_diverged:
                        downstream_file.name = upstream_name
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

                if downstream_file.external_data != upsteam_info:
                    downstream_file.external_data = upsteam_info
                    changed = True

                if changed:
                    downstream_file.external_update = make_aware(datetime.now())
                    downstream_file.save()

    for ifile in class_inst.files.filter(file__hash__in=removed):
        logger.warning(f"File {ifile} removed from {class_inst}")
        ifile.update(disappeared=True)
        continue
    class_inst.files.filter(file__hash__in=removed).update(disappeared=True)

    for hash in new:
        upsteam_info = upstream[hash]
        uploader_teacher = _closest_teacher(teachers, upsteam_info['uploader'])

        try:
            file = m.File.objects.get(hash=upsteam_info['hash'])
        except ObjectDoesNotExist:
            try:
                with reversion.create_revision():
                    file = m.File.objects.create(
                        size=upsteam_info['size'],
                        hash=upsteam_info['hash'],
                        mime=upsteam_info['mime'],
                        external_id=upsteam_info['id'],
                        # Obs: Files are being identified by hash, so there might be ignored IDs
                        iid=upsteam_info['id'],
                        external=True,
                        external_data={'upstream': upsteam_info})
            except IntegrityError as e:
                logger.error(f"Failed to sync the files of class instance {class_inst}")
                raise e
            logger.info(f"File {file} created")

        if not m.ClassFile.objects.filter(file=file, class_instance=class_inst).exists():
            with reversion.create_revision():
                m.ClassFile.objects.create(
                    file=file,
                    class_instance=class_inst,
                    category=upsteam_info['type'],
                    name=upsteam_info['name'],
                    official=True,
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
        logger.critical(f"Deleted enrollment (id:{external_id}) attempted to sync")
        return

    _upstream_sync_enrollment(upstream, external_id, class_inst)


def _request_enrollment(external_id):
    r = requests.get(f"http://{settings.CLIPY['host']}/enrollment/{external_id}")
    if r.status_code != 200:
        raise NetworkException(f"Unable to fetch enrollment {external_id}")
    return r.json()


def _upstream_sync_enrollment(upstream, external_id, class_inst):
    if class_inst is None:
        class_inst = m.ClassInstance.objects.get(external_id=upstream['class_instance_id'])
    if not all(
            k in upstream
            for k in ('id',
                      'approved', 'attempt',
                      'attendance', 'attendance_date',
                      'continuous_grade', 'continuous_grade_date',
                      'exam_grade', 'exam_grade_date',
                      'improvement_grade', 'improvement_grade_date',
                      'special_grade', 'special_grade_date',
                      'statutes', 'student', 'student_year')):
        logger.error(f"Invalid upstream enrollment data: {upstream}")
        return

    student_ext_id = upstream['student']
    attendance = upstream['attendance']
    attendance_date = upstream['attendance_date']
    normal_grade = upstream['continuous_grade']
    normal_grade_date = upstream['continuous_grade_date']
    recourse_grade = upstream['exam_grade']
    recourse_grade_date = upstream['exam_grade_date']
    special_grade = upstream['special_grade']
    special_grade_date = upstream['special_grade_date']
    improvement_grade = upstream['improvement_grade']
    improvement_grade_date = upstream['improvement_grade_date']

    if not (
            (isinstance(student_ext_id, int) or student_ext_id is None)
            and (isinstance(normal_grade, int) or normal_grade is None)
            and (isinstance(attendance, int) or attendance is None)
            and (isinstance(recourse_grade, int) or recourse_grade is None)
            and (isinstance(improvement_grade, int) or improvement_grade is None)
            and (isinstance(special_grade, int) or special_grade is None)):
        logger.error(f"Invalid upstream enrollment data: {upstream}")
        return

    try:
        student = m.Student.objects.get(external_id=student_ext_id)
    except ObjectDoesNotExist:
        student = sync_student(student_ext_id)

    if (student_year := upstream['student_year']) is not None:
        if student.year is None or student_year > student.year:
            logger.info(f"Updated student {student} year ({student.year} to {student_year})")
            student.year = student_year
            student.save(update_fields=['year'])

    grade = 0
    if attendance_date:
        attendance_date = make_aware(datetime.fromisoformat(attendance_date), is_dst=True)
    if normal_grade:
        grade = normal_grade
    if normal_grade_date:
        normal_grade_date = make_aware(datetime.fromisoformat(normal_grade_date), is_dst=True)
    if recourse_grade:
        grade = max(grade, recourse_grade)
    if recourse_grade_date:
        recourse_grade_date = make_aware(datetime.fromisoformat(recourse_grade_date), is_dst=True)
    if special_grade:
        grade = max(grade, special_grade)
    if special_grade_date:
        special_grade_date = make_aware(datetime.fromisoformat(special_grade_date), is_dst=True)
    if improvement_grade:
        grade = max(grade, improvement_grade)
    if improvement_grade_date:
        improvement_grade_date = make_aware(datetime.fromisoformat(improvement_grade_date), is_dst=True)

    approved = grade >= 10
    if approved != upstream['approved']:
        logger.debug(f'Upstream enrollment approval does not match the calculated one (enrollment {external_id}).')

    try:
        # Necessary against enrollments which changed twice upstream between syncs
        # (eg. enroll (id A) - sync - un-enroll - enroll (id B) - sync)
        m.Enrollment.objects \
            .filter(student=student, class_instance=class_inst) \
            .exclude(external_id=external_id) \
            .update(external_id=external_id, disappeared=False)

        obj = m.Enrollment.objects.get(external_id=external_id)
        changed = False
        with reversion.create_revision():
            for attr in ('normal_grade_date', 'recourse_grade_date', 'special_grade_date',
                         'improvement_grade_date', 'attendance', 'approved'):
                current = getattr(obj, attr)
                new = locals()[attr]
                if current != new:
                    setattr(obj, attr, new)
                    changed = True
            grades_changed = False
            for attr in ('normal_grade', 'recourse_grade', 'special_grade', 'improvement_grade', 'grade'):
                current = getattr(obj, attr)
                new = locals()[attr]

                if current != new:
                    logger.warning(f"{attr} from {current} to {new} in {obj}.")
                    setattr(obj, attr, new)
                    changed = True

            if obj.external_data != upstream:
                obj.external_data = upstream
                changed = True

            if changed:
                obj.save()

    except m.Enrollment.DoesNotExist:
        try:
            with reversion.create_revision():
                obj = m.Enrollment.objects.create(
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
                    improvement_grade=improvement_grade,
                    improvement_grade_date=improvement_grade_date,
                    approved=approved,
                    grade=grade,
                    external_id=external_id,
                    frozen=False,
                    external_update=make_aware(datetime.now()),
                    external_data={'upstream': upstream})
        except IntegrityError as e:
            logger.error(f"Failed to sync the enrollments of class instance {class_inst}")
            raise e
        logger.info(f"Inserted new enrollment {obj}")


def sync_shift(external_id, class_inst=None, recurse=Recursivity.NONE):
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
    r = requests.get(f"http://{settings.CLIPY['host']}/shift/{external_id}")
    if r.status_code != 200:
        raise NetworkException(f"Unable to fetch shift {external_id}")
    return r.json()


def _upstream_sync_shift_info(upstream, external_id, class_inst, recurse):
    invalid = not all(
        k in upstream
        for k in (
            'type', 'number', 'class_instance_id',
            'restrictions', 'state', 'instances',
            'students', 'teachers'))
    if invalid:
        logger.error(f"Invalid upstream shift instance data: {upstream}")
        return

    if class_inst.external_id != upstream['class_instance_id']:
        logger.critical("Consistency error. Shift upstream parent is not the local parent")
        return

    shift_type = upstream['type']
    if not (isinstance(shift_type, int) or shift_type < ctypes.ShiftType.min() or shift_type > ctypes.ShiftType.max()):
        logger.error("Unknown shift type: %s" % shift_type)

    upstream_details = {'state': upstream['state'], 'restrictions': upstream['restrictions']}
    try:
        obj = m.Shift.objects.get(class_instance=class_inst, external_id=external_id)
        if not obj.frozen and obj.external_data != upstream:
            with reversion.create_revision():
                obj.external_data = upstream_details
                obj.save()
    except ObjectDoesNotExist:
        with reversion.create_revision():
            obj = m.Shift.objects.create(
                class_instance=class_inst,
                shift_type=shift_type,
                number=upstream['number'],
                external_id=external_id,
                frozen=False,
                external_update=make_aware(datetime.now()),
                external_data={'upstream': upstream})
            logger.info(f"Shift {obj} created in {class_inst}")

    # ---------  Related shift instances ---------
    instances = obj.instances.exclude(external_id=None).all()

    new, disappeared, mirrored = _upstream_diff(set(instances), set(upstream['instances']))

    if m.ShiftInstance.objects.filter(external_id__in=new).exists():
        logger.critical(f"Some instances of shift {obj} belong to another shift: {new}")
        return

    if recurse == Recursivity.CREATION:
        for ext_id in new:
            sync_shift_instance(ext_id, shift=obj)
    elif recurse == Recursivity.FULL:
        for ext_id in chain(new, mirrored):
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
    from_time = upstream['from_time']

    if to_time is not None and from_time is None:
        logger.error(f"Consistency error syncing event id {external_id}. End time is set but start is not.")
        return

    if from_time is not None:
        from_time = datetime.strptime(from_time, "%H:%M")

    if to_time is not None:
        to_time = datetime.strptime(to_time, "%H:%M")
        duration = (to_time - from_time).seconds // 60
        from_time = from_time.time()  # Was a datetime

    if (upstream_info := upstream['info']) is not None:
        info = upstream_info + '.'
        if (upstream_note := upstream['note']) is not None:
            info = f'{info} {upstream_note}'
    else:
        info = None

    try:
        class_event = m.ClassInstanceEvent.objects.get(external_id=external_id)
        changed = False
        with reversion.create_revision():
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
                class_event.season = upstream['season']
                changed = True

            if class_event.external_data != upstream:
                class_event.external_data = upstream
                changed = True

            if changed:
                class_event.save()

    except m.ClassInstanceEvent.DoesNotExist:
        with reversion.create_revision():
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
                external_update=make_aware(datetime.now()),
                external_data={'upstream': upstream})
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
    r = requests.get(f"http://{settings.CLIPY['host']}/shift_inst/{external_id}")
    if r.status_code != 200:
        raise NetworkException(f"Unable to fetch shift instance {external_id}")
    return r.json()


def _upstream_sync_shift_instance(upstream, external_id, shift):
    if not all(k in upstream for k in ('shift', 'start', 'end', 'weekday', 'room')):
        logger.error(f"Invalid upstream shift instance data: {upstream}")
        return

    if shift.external_id != upstream['shift']:
        logger.critical("Consistency error. ShiftInstance upstream parent is not the local parent")
        return

    upstream_room = None
    online = False
    if (upstream_room_id := upstream['room']) is not None:
        try:
            upstream_room = m.Room.objects.get(external_id=upstream_room_id)
        except m.Room.DoesNotExist:
            if int(upstream_room_id) in (1665, 1666):
                # TODO use "online" & rm ^ this ^ awful hardcoding
                online = True
            else:
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
        with reversion.create_revision():
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
                    logger.warning(
                        f"Shift instance {shift_instance} is no longer in a room (was in {shift_instance.room})")
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

            if shift_instance.external_data != upstream:
                shift_instance.external_data = upstream
                changed = True

            if changed:
                shift_instance.save()
    except m.ShiftInstance.DoesNotExist:
        with reversion.create_revision():
            shift_instance = m.ShiftInstance.objects.create(
                shift=shift,
                weekday=upstream_weekday,
                start=upstream_start,
                duration=upstream_duration,
                room=upstream_room,
                external_id=external_id,
                frozen=False,
                external_update=make_aware(datetime.now()),
                external_data={'upstream': upstream})
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
    r = requests.get("http://%s/students/" % settings.CLIPY['host'])
    if r.status_code != 200:
        raise NetworkException("Unable to fetch students")
    return r.json()


def _upstream_sync_students(upstream_list):
    existing = {student.external_id: student for student in m.Student.objects.exclude(external_id=None).all()}

    for upstream in upstream_list:
        ext_id = upstream['id']
        if ext_id in existing:
            _upstream_sync_student(upstream, student=existing[ext_id])
        else:
            _upstream_sync_student(upstream)


def sync_student(external_id):
    """
    Synchronizes a single student to the current upstream
    """
    upstream = _request_student(external_id)
    return _upstream_sync_student(upstream)


def _request_student(external_id):
    r = requests.get(f"http://{settings.CLIPY['host']}/student/{external_id}")
    if r.status_code != 200:
        raise NetworkException("Unable to fetch students")
    return r.json()


def _upstream_sync_student(upstream, student=None):
    upstream_course = None
    if upstream_course_id := upstream['course']:
        try:
            upstream_course = m.Course.objects.get(external_id=upstream_course_id)
        except m.Course.DoesNotExist:
            logger.error(f'Upstream course {upstream_course_id} is not imported')

    if student:
        changed = False
        with reversion.create_revision():
            if (upstream_abbr := upstream['abbr']) is not None:
                if student.abbreviation != upstream_abbr:
                    logger.warning(f'Student {student} abbreviation changed '
                                   f'("{student.abbreviation}" to "{upstream_abbr}").')
                student.abbreviation = upstream_abbr
                changed = True
            if upstream_course:
                if not student.course or student.course != upstream_course:
                    student.course = upstream_course
                    changed = True
            if (upstream_name := upstream['name']) is not None:
                if student.name != upstream_name:
                    logger.warning(f"Student {student} name changed "
                                   f"from {student.external_data['name']} to {upstream_name}")
                    student.name = upstream_name
                    changed = True

            if student.external_data != upstream:
                student.external_data = upstream
                changed = True

            if changed:
                student.save()
        return student
    else:
        with reversion.create_revision():
            student = m.Student.objects.create(
                name=upstream['name'],
                abbreviation=upstream['abbr'],
                iid=upstream['id'],
                number=upstream['id'],
                course=upstream_course,
                external_id=upstream['id'],
                external_update=make_aware(datetime.now()),
                external_data={'upstream': upstream})
            logger.info(f'Created student {student}.')
        return student


def sync_teachers():
    """
    Synchronizes teachers to the current upstream
    """
    # TODO this method is essentially a duplication of sync_students. Figure a way to generify both
    upstream = _request_teachers()
    _upstream_sync_teachers(upstream)


def _request_teachers():
    r = requests.get("http://%s/teachers/" % settings.CLIPY['host'])
    if r.status_code != 200:
        raise NetworkException("Unable to fetch teachers")
    return r.json()


def _upstream_sync_teachers(upstream_list):
    for entry in upstream_list:
        if not all(k in entry for k in ('id', 'name', 'first_year', 'last_year', 'depts')):
            logger.error(f"Invalid upstream teacher data: {entry}")
            return

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
            changed = False
            with reversion.create_revision():
                if (upstream_name := upstream['name']) is not None:
                    if obj.name != upstream_name:
                        if obj.name is not None:
                            logger.warning(f"Teacher {obj} name changed from {obj.name} to {upstream_name}")
                        obj.name = upstream_name
                        changed = True

                if obj.external_data != upstream:
                    obj.external_data = upstream
                    changed = True

                if changed:
                    obj.save()

        else:
            with reversion.create_revision():
                obj = m.Teacher.objects.create(
                    name=upstream['name'],
                    iid=upstream['id'],
                    external_id=upstream['id'],
                    external_update=make_aware(datetime.now()),
                    external_data={'upstream': upstream})
                logger.info(f'Created teacher {obj}.')

        current_departments = obj.departments.all()
        new, disappeared, _ = _upstream_diff(current_departments, upstream_dept_ids)
        m.Teacher.departments.through.objects.filter(teacher=obj, department__external_id__in=disappeared).delete()
        m.Teacher.departments.through.objects.bulk_create(
            map(lambda department_id: m.Teacher.departments.through(department_id=department_id, teacher=obj),
                m.Department.objects.filter(external_id__in=new).values_list('id', flat=True)))


def calculate_active_classes():
    today = date.today()
    current_year = today.year + (today.month > 8)
    for klass in m.Class.objects.all():
        class_meta = klass.instances.aggregate(max_year=Max('year'))  # , max_date=Max('period_instance__date_to'))
        last_year = class_meta['max_year']
        # TODO get rid of magic number
        has_recent_enrollments = klass.instances \
            .filter(year__gte=current_year - 2) \
            .order_by('year') \
            .annotate(enrollment_count=Sum('enrollments')) \
            .exclude(enrollment_count=0) \
            .exists()
        extinguished = not (last_year == current_year or has_recent_enrollments)
        if extinguished != klass.extinguished:
            klass.extinguished = extinguished
            klass.save(update_fields=['extinguished'])


def request_courses_update():
    _update(f"http://{settings.CLIPY['host']}/update/courses/")


def request_rooms_update():
    _update(f"http://{settings.CLIPY['host']}/update/rooms/")


def request_admissions_update():
    _update(f"http://{settings.CLIPY['host']}/update/admissions/")


def request_teachers_update(department):
    _update(f"http://{settings.CLIPY['host']}/update/teachers/{department}")


def request_classes_update():
    _update(f"http://{settings.CLIPY['host']}/update/classes/")


def request_class_instance_update(external_id, update_info=False, update_enrollments=False, update_shifts=False,
                                  update_events=False, update_files=False, update_grades=False):
    """
    :param external_id: The foreign id of the class instance that is being sync'd
    :param update_info: Whether to request CLIPy to update the class info from CLIP before updating Supernova's
    :param update_enrollments: Whether to request CLIPy to update the class enrollments from CLIP before updating Supernova's
    :param update_shifts: Whether to request CLIPy to update the class shifts from CLIP before updating Supernova's
    :param update_events: Whether to request CLIPy to update the class events from CLIP before updating Supernova's
    :param update_files: Whether to request CLIPy to update this information from CLIP before updating Supernova's
    """

    if update_info:
        _update(f"http://{settings.CLIPY['host']}/update/class_info/{external_id}")
    if update_enrollments:
        _update(f"http://{settings.CLIPY['host']}/update/class_enrollments/{external_id}")
    if update_shifts:
        _update(f"http://{settings.CLIPY['host']}/update/shifts/{external_id}")
    if update_events:
        _update(f"http://{settings.CLIPY['host']}/update/events/{external_id}")
    if update_grades:
        _update(f"http://{settings.CLIPY['host']}/update/class_grades/{external_id}")
    if update_files:
        _update(f"http://{settings.CLIPY['host']}/update/class_files/{external_id}")


def _update(url):
    status_code = requests.get(url).status_code
    if status_code != 200:
        logger.error(f"Endpoint {url} failed to update. Status code {status_code}")


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
    if uploader_teacher is None:
        name_filter = reduce(lambda x, y: x & y, [Q(name__contains=word) for word in name.split(' ')])
        matches = m.Teacher.objects.filter(name_filter).all()
        if len(matches) == 1:
            uploader_teacher = matches[0]

    return uploader_teacher
