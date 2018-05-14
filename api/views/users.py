from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import users as serializers
from users.utils import get_network_identifier
from users import models as users


class ProfileDetailed(APIView):
    def get(self, request, nickname, format=None):  # TODO authentication
        user = users.User.objects.get(nickname=nickname)
        serializer = serializers.ProfileDetailedSerializer(user)
        return Response(serializer.data)


class UserSocialNetworks(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

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
