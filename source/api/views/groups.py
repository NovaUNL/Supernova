from django.db import IntegrityError
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import groups as serializers
from groups import models as m
from users import models as users


class GroupList(APIView):
    def get(self, request, format=None):
        serializer = serializers.GroupTypeSerializer(m.Group.objects.all(), many=True)
        return Response(serializer.data)


class GroupSubscription(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, abbr):
        group = get_object_or_404(m.Group, abbreviation=abbr)
        is_subscribed = users.Subscription.objects.filter(group=group, subscriber=request.user).exists()
        return Response(is_subscribed)

    def post(self, request, abbr):
        group = get_object_or_404(m.Group, abbreviation=abbr)
        is_subscribed = users.Subscription.objects.filter(group=group, subscriber=request.user).exists()
        if not is_subscribed:
            try:
                users.Subscription.objects.create(to=group, subscriber=request.user)
            except IntegrityError:
                return Response(status=409)
        return Response()

    def delete(self, request, abbr):
        group = get_object_or_404(m.Group, abbreviation=abbr)
        users.Subscription.objects.filter(group=group, subscriber=request.user).delete()
        return Response()


class GroupMembershipRequest(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, abbr):
        group = get_object_or_404(m.Group, abbreviation=abbr)
        openness = group.outsiders_openness
        if group.outsiders_openness == m.Group.REQUEST:
            has_requested = m.MembershipRequest.objects.filter(group=group, user=request.user).exists()
        else:
            has_requested = False
        return Response({'openness': openness, 'requested': has_requested})

    def post(self, request, abbr):
        group = get_object_or_404(m.Group, abbreviation=abbr)
        if m.Membership.objects.filter(member=request.user, group=group).exists():
            raise Response("Membership already exists", status=409)

        if group.outsiders_openness == m.Group.OPEN:
            if group.default_role_id is None:
                raise Response("Group has no default role", status=502)
            else:
                m.Membership.objects.create(member=request.user, group=group, role_id=group.default_role_id)
                raise Response()
        elif group.outsiders_openness == m.Group.REQUEST:
            has_requested = m.MembershipRequest.objects.filter(group=group, user=request.user).exists()
            if has_requested:
                return Response(status=409)
            if 'message' in request.POST:
                message = request.POST['message']
                if isinstance(message, str):
                    message = message.strip()
                    m.MembershipRequest.objects.create(group=group, user=request.user, message=message)
                else:
                    return Response(status=400)
            m.MembershipRequest.objects.create(group=group, user=request.user)
        else:
            return Response("Group has restricted access", status=403)
        return Response()

    def delete(self, request, abbr):
        group = get_object_or_404(m.Group, abbreviation=abbr)
        # Only delete requests without a verdict
        m.MembershipRequest.objects.filter(group=group, user=request.user, granted=None).delete()
        return Response()
