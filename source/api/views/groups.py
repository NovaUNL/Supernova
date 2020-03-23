from datetime import datetime, timedelta

from rest_framework import authentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from api import permissions
from api.serializers import groups as serializers
from api.utils import get_weekday_occurrences
from groups import models as m


class GroupList(APIView):
    def get(self, request, format=None):
        serializer = serializers.GroupTypeSerializer(m.Group.objects.all(), many=True)
        return Response(serializer.data)

@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
def group_schedule(_, abbr, from_date, to_date):
    weekday_occurrences = get_weekday_occurrences(from_date, to_date)

    group = get_object_or_404(m.Group, abbreviation=abbr)
    once_schedule_entries = m.ScheduleOnce.objects.filter(group=group)
    periodic_schedule_entries = m.SchedulePeriodic.objects.filter(group=group)

    schedule_entries = []
    for entry in once_schedule_entries:
        title = entry.title

        schedule_entries.append({
            'id': f"GO{entry.id}",
            'type': 'GO',
            'title': title,
            'start': entry.datetime.replace(tzinfo=None),
            'end': entry.datetime.replace(tzinfo=None) + timedelta(minutes=entry.duration)
        })

    for entry in periodic_schedule_entries:
        duration_delta = timedelta(minutes=entry.duration)
        for day in weekday_occurrences[entry.weekday]:
            if not (entry.start_date <= day <= entry.end_date):
                continue
            start_datetime = datetime.combine(day, entry.time)
            schedule_entries.append({
                'id': f"GP{datetime.strftime(day, '%y%m%d')}{entry.id}",
                'type': 'GP',
                'title': entry.title,
                'start': start_datetime,
                'end': start_datetime + duration_delta
            })
    schedule_entries = sorted(schedule_entries, key=lambda occurrence: occurrence['start'])
    return Response(schedule_entries)
