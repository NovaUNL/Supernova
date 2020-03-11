from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import services as serializers
from services import models as services


class ServiceList(APIView):
    def get(self, request, format=None):
        serializer = serializers.ServiceWithBuildingSerializer(
            services.Service.objects.filter(bar__isnull=True).all(), many=True)
        return Response(serializer.data)


class BarList(APIView):
    def get(self, request, format=None):
        serializer = serializers.ServiceWithBuildingSerializer(
            services.Service.objects.filter(bar__isnull=False).all(), many=True)
        return Response(serializer.data)