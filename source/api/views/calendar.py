from django.db.models import F
from django.conf import settings

from rest_framework import authentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from api import permissions
from users.utils import get_students
from users import models as users
from college import models as college
from groups import models as groups


@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
@permission_classes((permissions.SelfOnly,))
def user_schedule(_, nickname):
    """
    Exposes the periodic events that are related to a user
    :param nickname: User nickname
    :return: Response with the current and historical events
    """
    user = get_object_or_404(users.User.objects.prefetch_related('students', 'groups_custom'), nickname=nickname)
    primary_students, _ = get_students(user)
    user_groups = user.groups_custom.all()
    schedule_entries = []

    shift_instances = college.ShiftInstance.objects \
        .select_related('shift__class_instance__parent') \
        .prefetch_related('room__building') \
        .filter(shift__student__in=primary_students,
                shift__class_instance__year=settings.COLLEGE_YEAR,
                shift__class_instance__period=settings.COLLEGE_PERIOD) \
        .annotate(end=F('start') - F('duration')) \
        .all()
    for instance in shift_instances:
        schedule_entries.append({
            'type': instance.shift.type_abbreviation,
            'title': instance.title,
            'weekday': instance.weekday,
            'time': instance.start_str,
            'duration': instance.duration,
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

    return Response(schedule_entries)


@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
@permission_classes((permissions.SelfOnly,))
def user_calendar(_, nickname):
    """
    Exposes every event that is related to a user, both periodic and spontaneous ("once")
    :param nickname: User nickname
    :return: Response with the events that compose the user calendar.
    """
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
        .annotate(end=F('start') - F('duration')) \
        .all()

    for instance in shift_instances:
        schedule_entries.append({
            'type': instance.shift.type_abbreviation,
            'title': instance.title,
            'weekday': instance.weekday,
            'time': instance.start_str,
            'duration': instance.duration,
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

    return Response(schedule_entries)



@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
def group_schedule(_, abbr):
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