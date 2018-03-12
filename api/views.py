from django.contrib.auth.models import User, Group
from rest_framework import viewsets

# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#
#
# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ServiceWithBuildingSerializer, DepartmentSerializer, BuildingWithServicesSerializer, \
    BuildingMinimalSerializer, DepartmentMinimalSerializer, CourseSerializer, SynopsisAreaSerializer, \
    SynopsisTopicSectionsSerializer
from kleep.models import Bar, Service, Building, Department, Course, Class, SynopsisArea, SynopsisTopic


# class GroupViewSet(viewsets.ModelViewSet):
#     queryset = Bar.objects.all()
#     serializer_class = BarSerializer


class BuildingList(APIView):
    def get(self, request, format=None):
        serializer = BuildingWithServicesSerializer(Building.objects.all(), many=True)
        return Response(serializer.data)


class CampusMap(APIView):
    def get(self, request, format=None):
        serializer = BuildingMinimalSerializer(Building.objects.all(), many=True)
        return Response({'map_url': 'https://gitlab.com/claudiop/KleepAssets/raw/master/Campus.svg',
                         'buildings': serializer.data})


class ServiceList(APIView):
    def get(self, request, format=None):
        serializer = ServiceWithBuildingSerializer(Service.objects.filter(bar__isnull=True).all(), many=True)
        return Response(serializer.data)


class BarList(APIView):
    def get(self, request, format=None):
        serializer = ServiceWithBuildingSerializer(Service.objects.filter(bar__isnull=False).all(), many=True)
        return Response(serializer.data)


class DepartmentList(APIView):
    def get(self, request, format=None):
        serializer = DepartmentMinimalSerializer(Department.objects.all(), many=True)
        return Response(serializer.data)


class DepartmentDetailed(APIView):
    def get(self, request, pk, format=None):
        serializer = DepartmentSerializer(Department.objects.get(id=pk))
        return Response(serializer.data)


class CourseDetailed(APIView):
    def get(self, request, pk, format=None):
        course = Course.objects.get(id=pk)
        data = CourseSerializer(course).data
        data['degree'] = course.degree.name
        return Response(data)


class ClassDetailed(APIView):
    def get(self, request, pk, format=None):
        serializer = CourseSerializer(Class.objects.get(id=pk))
        return Response(serializer.data)


class SyopsesAreas(APIView):
    def get(self, request, format=None):
        serializer = SynopsisAreaSerializer(SynopsisArea.objects.all(), many=True)
        return Response(serializer.data)


class SyopsesTopicSections(APIView):
    def get(self, request, pk, format=None):
        serializer = SynopsisTopicSectionsSerializer(SynopsisTopic.objects.get(id=pk))
        return Response(serializer.data)
