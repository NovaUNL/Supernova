from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import groups as serializers
from groups import models as groups


class GroupList(APIView):
    def get(self, request, format=None):
        serializer = serializers.GroupTypeSerializer(groups.Group.objects.all(), many=True)
        return Response(serializer.data)
