from django.conf import settings
from django.core.cache import cache

from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api import permissions
from college.choice_types import RoomType
from users.utils import get_students
from users import models as users
from college import models as college
from groups import models as groups
from api.serializers import college as college_serializer


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_schedule(request, nickname):
    """
    Exposes the periodic events that are related to a user
    :param nickname: User nickname
    :return: Response with the current and historical events
    """
    cache_key = f'user_{nickname}_schedule'
    user_schedule = cache.get(cache_key)
    if user_schedule is None:
        user = get_object_or_404(users.User.objects.prefetch_related('students', 'groups_custom'), nickname=nickname)
    else:
        user = get_object_or_404(users.User, nickname=nickname)

    permissions = user.profile_permissions_for(request.user)
    if not permissions['schedule_visibility']:
        raise PermissionDenied(detail=f'{request.user.nickname} atempted to view {user.nickname} schedule.')

    if user_schedule:
        return Response(user_schedule)

    primary_students, _ = get_students(user)
    user_groups = user.groups_custom.all()
    schedule_entries = []

    shift_instances = college.ShiftInstance.objects \
        .select_related('shift__class_instance__parent') \
        .prefetch_related('room__building') \
        .filter(shift__student__in=primary_students,
                shift__class_instance__year=settings.COLLEGE_YEAR,
                shift__class_instance__period=settings.COLLEGE_PERIOD) \
        .all()
    for instance in shift_instances:
        schedule_entries.append({
            'type': instance.shift.type_abbreviation,
            'title': instance.title,
            'weekday': instance.weekday,
            'time': instance.start_str,
            'duration': instance.duration,
            'url': instance.shift.get_absolute_url(),
        })

    own_periodic_schedule_entries = users.SchedulePeriodic.objects.filter(user=user)
    for entry in own_periodic_schedule_entries:
        schedule_entries.append({
            'type': 'U',
            'title': entry.title,
            'weekday': entry.weekday,
            'time': entry.time,
            'duration': entry.duration,
            'start': entry.start_date,
            'end': entry.end_date,
        })

    group_periodic_schedule_entries = groups.SchedulePeriodic.objects.filter(group__in=user_groups)
    for entry in group_periodic_schedule_entries:
        schedule_entries.append({
            'type': 'G',
            'title': entry.title,
            'weekday': entry.weekday,
            'time': entry.time,
            'duration': entry.duration,
            'start': entry.start_date,
            'end': entry.end_date,
        })

    cache.set(cache_key, schedule_entries, timeout=60 * 60)
    return Response(schedule_entries)


@api_view(['GET'])
@permission_classes((permissions.SelfOnly,))
def user_calendar(_, nickname):
    """
    Exposes every event that is related to a user, both periodic and spontaneous ("once")
    :param nickname: User nickname
    :return: Response with the events that compose the user calendar.
    """
    cache_key = f'user_{nickname}_calendar'
    user_calendar = cache.get(cache_key)
    if user_calendar is not None:
        Response(user_calendar)

    user = get_object_or_404(users.User.objects.prefetch_related('students', 'memberships'), nickname=nickname)
    user_groups = user.groups_custom.all()
    primary_students, _ = get_students(user)
    schedule_entries = []

    shift_instances = college.ShiftInstance.objects \
        .select_related('shift__class_instance__parent') \
        .prefetch_related('room__building') \
        .filter(shift__student__in=primary_students,
                shift__class_instance__year=settings.COLLEGE_YEAR,
                shift__class_instance__period=settings.COLLEGE_PERIOD) \
        .all()

    for instance in shift_instances:
        schedule_entries.append({
            'type': instance.shift.type_abbreviation,
            'title': instance.title,
            'weekday': instance.weekday,
            'time': instance.start_str,
            'duration': instance.duration,
            'url': instance.shift.get_absolute_url(),
        })
    own_once_schedule_entries = users.ScheduleOnce.objects.filter(user=user)
    for entry in own_once_schedule_entries:
        schedule_entries.append({
            'type': 'U',
            'title': entry.title,
            'datetime': entry.datetime.isoformat().split('+')[0],
            'duration': entry.duration,
        })
    own_periodic_schedule_entries = users.SchedulePeriodic.objects.filter(user=user)
    for entry in own_periodic_schedule_entries:
        schedule_entries.append({
            'type': 'U',
            'title': entry.title,
            'weekday': entry.weekday,
            'time': entry.time,
            'duration': entry.duration,
            'start': entry.start_date,
            'end': entry.end_date,
        })
    group_once_schedule_entries = groups.ScheduleOnce.objects.filter(group__in=user_groups)
    for entry in group_once_schedule_entries:
        schedule_entries.append({
            'type': 'G',
            'title': entry.title,
            'datetime': entry.datetime.isoformat().split('+')[0],
            'duration': entry.duration,
        })
    group_periodic_schedule_entries = groups.SchedulePeriodic.objects.filter(group__in=user_groups)
    for entry in group_periodic_schedule_entries:
        schedule_entries.append({
            'type': 'G',
            'title': entry.title,
            'weekday': entry.weekday,
            'time': entry.time,
            'duration': entry.duration,
            'start': entry.start_date,
            'end': entry.end_date,
        })
    class_events = college.ClassInstanceEvent.objects \
        .select_related('class_instance__parent') \
        .filter(class_instance__enrollments__student__in=primary_students)
    for event in class_events:
        schedule_entries.append({
            'type': 'CE',
            'title': str(event),
            'datetime': event.datetime_str,
            'duration': event.duration if event.duration else 0,
        })

    cache.set(cache_key, schedule_entries, timeout=60 * 60)
    return Response(schedule_entries)


@api_view(['GET'])
def group_calendar(_, abbr):
    group = get_object_or_404(groups.Group, abbreviation=abbr)

    schedule_entries = []

    group_once_schedule_entries = groups.ScheduleOnce.objects.filter(group=group)

    for entry in group_once_schedule_entries:
        schedule_entries.append({
            'type': 'G',
            'title': entry.title,
            'datetime': entry.datetime.isoformat().split('+')[0],
            'duration': entry.duration,
        })
    group_periodic_schedule_entries = groups.SchedulePeriodic.objects.filter(group=group)
    for entry in group_periodic_schedule_entries:
        schedule_entries.append({
            'type': 'G',
            'title': entry.title,
            'weekday': entry.weekday,
            'time': entry.time,
            'duration': entry.duration,
            'start': entry.start_date,
            'end': entry.end_date,
        })
    return Response(schedule_entries)


@api_view(['GET'])
def building_schedule_shifts_view(request, building_id):
    building = get_object_or_404(college.Building, id=building_id)

    shift_instances = college.ShiftInstance.objects \
        .select_related('shift__class_instance__parent') \
        .filter(room__building=building,
                shift__class_instance__year=settings.COLLEGE_YEAR,
                shift__class_instance__period=settings.COLLEGE_PERIOD)\
        .exclude(weekday=None) \
        .all()
    schedule_entries = []
    for instance in shift_instances:
        schedule_entries.append({
            'resourceId': instance.room_id,
            'title': instance.short_title,
            'daysOfWeek': instance.weekday_as_arr,
            'startTime': instance.start_str,
            'endTime': instance.end_str,
            'url': instance.shift.get_absolute_url(),
        })
    return Response(schedule_entries)


@api_view(['GET'])
def building_schedule_rooms_view(request, building_id):
    building = get_object_or_404(college.Building, id=building_id)
    rooms = college.Room.objects \
        .filter(building=building, type__in=(RoomType.CLASSROOM, RoomType.AUDITORIUM, RoomType.LABORATORY)) \
        .exclude()
    serializer = college_serializer.NestedRoomSerializer(rooms, many=True)
    return Response(serializer.data)
