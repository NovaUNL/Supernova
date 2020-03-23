from datetime import timedelta

from rest_framework import authentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from api import permissions
from api.serializers import groups as serializers
from api.schedule_utils import get_weekday_occurrences, append_schedule_entries, append_periodic_schedule_entries_in_extension
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
    append_schedule_entries(schedule_entries, once_schedule_entries)
    append_periodic_schedule_entries_in_extension(schedule_entries, periodic_schedule_entries, weekday_occurrences)
    schedule_entries = sorted(schedule_entries, key=lambda occurrence: occurrence['start'])
    return Response(schedule_entries)
