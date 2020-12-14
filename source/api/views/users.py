from datetime import datetime

from django.utils import timezone
from django.core.cache import cache

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import ParseError, ValidationError, PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import users as serializers
from api import permissions
from users.utils import get_network_identifier
from users import models as users


class ProfileDetailed(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.SelfOnly,)

    def get(self, request, nickname):  # TODO authentication
        user = users.User.objects.get(nickname=nickname)
        serializer = serializers.ProfileDetailedSerializer(user)
        return Response(serializer.data)




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
        if profile is None:
            raise ValidationError(f"Bad profile ('{request.data['profile']}')")
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


class UserNotificationList(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get(self, request):
        timestamp = int(datetime.now().replace(tzinfo=timezone.utc).timestamp())
        notification_list = cache.get('%s_notification_list' % request.user.id)
        if notification_list is None:
            notifications = users.Notification.objects \
                .filter(receiver=request.user, dismissed=False) \
                .order_by('issue_timestamp') \
                .reverse()
            notification_list = list(map(lambda n: n.to_api(), notifications))
            cache.set('%s_notification_list' % request.user.id, notification_list)
        return Response({'notifications': notification_list, 'timestamp': timestamp})

    def delete(self, request):
        if 'timestamp' in request.data:
            timestamp = timezone.make_aware(datetime.fromtimestamp(request.data['timestamp']))
            users.Notification.objects \
                .filter(receiver=request.user, issue_timestamp__lte=timestamp) \
                .update(dismissed=True)
        else:
            users.Notification.objects.filter(receiver=request.user).update(dismissed=True)
        request.user.clear_notification_cache()
        return Response()


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
