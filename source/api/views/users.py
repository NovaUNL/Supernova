from datetime import datetime, timedelta

from django.db.models import F
from rest_framework import authentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

import settings
from api.serializers import users as serializers
from api import permissions
from users.utils import get_network_identifier, get_students
from users import models as users
from college import models as college


class ProfileDetailed(APIView):
    def get(self, request, nickname, format=None):  # TODO authentication
        user = users.User.objects.get(nickname=nickname)
        serializer = serializers.ProfileDetailedSerializer(user)
        return Response(serializer.data)


@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
@permission_classes((permissions.SelfOnly,))
def user_schedule(_, nickname, from_date, to_date):
    try:
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')
    except ValueError:
        raise ValidationError(detail="Bad date range")
    if to_date < from_date:
        raise ValidationError(detail="Range goes back in time")

    delta: timedelta = to_date - from_date
    if delta.days > 31:
        raise ValidationError(detail="Range exceeds limit")

    weekday_occurrences = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    day = from_date
    for _ in range(delta.days):
        weekday_occurrences[day.weekday()].append(day)
        day = day + timedelta(days=1)

    user = get_object_or_404(users.User.objects.prefetch_related('students'), nickname=nickname)
    primary_students, _ = get_students(user)

    turn_instances = college.TurnInstance.objects \
        .select_related('turn__class_instance__parent') \
        .prefetch_related('room__building') \
        .filter(turn__student__in=primary_students,
                turn__class_instance__year=settings.COLLEGE_YEAR,
                turn__class_instance__period=settings.COLLEGE_PERIOD) \
        .annotate(end=F('start') - F('duration')) \
        .all()
    turn_instance_occurrences = []
    for instance in turn_instances:
        instance: college.TurnInstance
        start_delta = timedelta(minutes=instance.start)
        duration_delta = timedelta(minutes=instance.duration)
        title = f'{instance.turn.class_instance.parent.abbreviation} {instance.turn.get_turn_type_display()}'

        for day in weekday_occurrences[instance.weekday]:
            start = day + start_delta
            end = start + duration_delta
            turn_instance_occurrences.append({
                'id': f"A{datetime.strftime(start, '%y%m%d')}{instance.id}",
                'type': instance.turn.type_abbreviation,
                'title': title,
                'start': start,
                'end': end
            })
    turn_instance_occurrences = sorted(turn_instance_occurrences, key=lambda occurrence: occurrence['start'])
    return Response(turn_instance_occurrences)


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
