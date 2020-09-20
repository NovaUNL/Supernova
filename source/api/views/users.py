from django.core.cache import cache
from django.db.models import F
from rest_framework import authentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import ParseError, ValidationError, PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import settings
from api.serializers import users as serializers
from api import permissions
from api.schedule_utils import get_weekday_occurrences, append_turn_instances, append_schedule_entries, \
    append_periodic_schedule_entries_in_extension
from users.utils import get_network_identifier, get_students
from users import models as users
from college import models as college
from groups import models as groups


class ProfileDetailed(APIView):
    def get(self, request, nickname, format=None):  # TODO authentication
        user = users.User.objects.get(nickname=nickname)
        serializer = serializers.ProfileDetailedSerializer(user)
        return Response(serializer.data)


@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
@permission_classes((permissions.SelfOnly,))
def user_schedule(_, nickname, from_date, to_date):
    weekday_occurrences = get_weekday_occurrences(from_date, to_date)
    user = get_object_or_404(users.User.objects.prefetch_related('students', 'memberships'), nickname=nickname)
    primary_students, _ = get_students(user)

    turn_instances = college.TurnInstance.objects \
        .select_related('turn__class_instance__parent') \
        .prefetch_related('room__building') \
        .filter(turn__student__in=primary_students,
                turn__class_instance__year=settings.COLLEGE_YEAR,
                turn__class_instance__period=settings.COLLEGE_PERIOD) \
        .annotate(end=F('start') - F('duration')) \
        .all()
    schedule_entries = []

    append_turn_instances(schedule_entries, turn_instances, weekday_occurrences)
    user_groups = user.memberships.all()
    once_schedule_entries = groups.ScheduleOnce.objects.filter(group__in=user_groups)
    periodic_schedule_entries = groups.SchedulePeriodic.objects.filter(group__in=user_groups)
    append_schedule_entries(schedule_entries, once_schedule_entries)
    append_periodic_schedule_entries_in_extension(schedule_entries, periodic_schedule_entries, weekday_occurrences)
    schedule_entries = sorted(schedule_entries, key=lambda occurrence: occurrence['start'])
    return Response(schedule_entries)


class UserSocialNetworks(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.SelfOnly,)

    def get(self, request, nickname, format=None):  # TODO restrict to privacy level
        user = users.User.objects.get(nickname=nickname)
        serializer = serializers.SocialNetworksSerializer(user.social_networks, many=True)
        return Response(serializer.data)

    def put(self, request, nickname, format=None):  # TODO restrict to owner
        user = users.User.objects.get(nickname=nickname)
        if 'profile' not in request.data or 'network' not in request.data:
            raise ParseError()
        try:
            network = int(request.data['network'])
        except TypeError:
            raise ParseError()
        if network >= len(users.SocialNetworkAccount.SOCIAL_NETWORK_CHOICES):
            raise ValidationError("Unknown network")
        profile = get_network_identifier(network, request.data['profile'])
        if users.SocialNetworkAccount.objects.filter(user=user, network=network, profile=profile).exists():
            raise ValidationError("Duplicated network")

        users.SocialNetworkAccount(user=user, network=network, profile=profile).save()
        return Response({'profile': profile, 'network': network})

    def delete(self, request, nickname, format=None):
        user = users.User.objects.get(nickname=nickname)
        if 'profile' not in request.data or 'network' not in request.data:
            raise ParseError()
        network = request.data['network']
        if network >= len(users.SocialNetworkAccount.SOCIAL_NETWORK_CHOICES):
            raise ValidationError("Unknown network")
        profile = get_network_identifier(request.data['network'], request.data['profile'])
        if not users.SocialNetworkAccount.objects.filter(user=user, network=network, profile=profile).exists():
            raise ValidationError("Not found")
        users.SocialNetworkAccount.objects.filter(user=user, network=network, profile=profile).delete()


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def notification_count_view(request):
    notification_count = cache.get('%s_notification_count' % request.user.id)
    if notification_count is None:
        count = users.Notification.objects.filter(receiver=request.user, dismissed=False).count()
        cache.set('%s_notification_count' % request.user.nickname, count)
        return Response(count)
    return Response(notification_count)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def notification_list_view(request):
    notification_list = cache.get('%s_notification_list' % request.user.id)
    if notification_list is None:
        notifications = users.Notification.objects\
            .filter(receiver=request.user, dismissed=False)\
            .order_by('issue_timestamp')\
            .reverse()
        notifications = list(map(lambda n: n.to_api(), notifications))
        cache.set('%s_notification_list' % request.user.id, notifications)
        return Response(notifications)
    return Response(notification_list)


class UserModeration(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAdminUser,)

    def get(self, request, user_id, format=None):
        user = users.User.objects.get(id=user_id)
        return Response({'active': user.is_active})

    def post(self, request, user_id, format=None):
        user = users.User.objects.get(id=user_id)
        if user.is_staff:
            raise PermissionDenied("Cannot take actions against administrators")
        if not (isinstance(request.data, dict) and 'action' in request.data):
            raise ParseError()
        action = request.data['action']
        if action == 'suspend':
            user.is_active = False
        elif action == 'unsuspend':
            user.is_active = True
        user.save()
        return Response("Ok")
