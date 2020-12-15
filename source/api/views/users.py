from datetime import datetime

from django.utils import timezone
from django.core.cache import cache

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import ParseError, ValidationError, PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404

from api.serializers import users as serializers
from api import permissions
from users.utils import get_network_identifier
from users import models as users


class ProfileDetailed(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.SelfOnly,)

    def get(self, request, nickname):  # TODO authentication
        user = get_object_or_404(users.User, nickname=nickname)
        serializer = serializers.ProfileDetailedSerializer(user)
        return Response(serializer.data)


class UserExternalPages(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.SelfOnly,)

    def get(self, request, nickname):  # TODO restrict to privacy level
        user = get_object_or_404(users.User, nickname=nickname)
        serializer = serializers.ExternalPageSerializer(user.external_pages, many=True)
        return Response(serializer.data)

    def put(self, request, nickname):  # TODO restrict to owner
        user = get_object_or_404(users.User, nickname=nickname)
        if 'url' not in request.data:
            raise Response(status=400)

        page = users.ExternalPage.objects.create(user=user, url=request.data['url'])
        serializer = serializers.ExternalPageSerializer(page)
        return Response(serializer.data)

    def delete(self, request, nickname):
        user = get_object_or_404(users.User, nickname=nickname)
        if 'id' not in request.data:
            raise Response(status=400)
        page = get_object_or_404(users.ExternalPage, id=request.data['id'], user=user)
        page.delete()
        return Response()


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
