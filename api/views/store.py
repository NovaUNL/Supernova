from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import store as serializers
from store import models as store


class Store(APIView):
    def get(self, request, format=None):
        serializer = serializers.StoreItemSerializer(store.Item.objects.all(), many=True)
        return Response(serializer.data)
