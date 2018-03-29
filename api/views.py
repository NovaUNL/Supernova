from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ServiceWithBuildingSerializer, DepartmentSerializer, BuildingWithServicesSerializer, \
    BuildingMinimalSerializer, DepartmentMinimalSerializer, CourseSerializer, SynopsisAreaSerializer, \
    SynopsisTopicSectionsSerializer, NewsSerializer, NewsMinimalSerializer, GroupTypeSerializer, \
    StoreItemSerializer, BarListMenusSerializer, ProfileMinimalSerializer, ProfileDetailedSerializer
from kleep.models import Bar, Service, Building, Department, Course, Class, \
    GroupType, Profile
from news.models import NewsItem
from store.models import StoreItem
from synopses.models import SynopsisArea, SynopsisTopic


class BuildingList(APIView):
    def get(self, request, format=None):
        serializer = BuildingWithServicesSerializer(Building.objects.all(), many=True)
        return Response(serializer.data)


class BuildingDetailed(APIView):
    def get(self, request, pk, format=None):
        serializer = BuildingWithServicesSerializer(Building.objects.get(pk=pk))
        return Response(serializer.data)


class CampusMap(APIView):
    def get(self, request, format=None):
        serializer = BuildingMinimalSerializer(Building.objects.all(), many=True)
        return Response({'map_url': 'https://gitlab.com/claudiop/KleepAssets/raw/master/Campus.svg',
                         'buildings': serializer.data})


class TransportationMap(APIView):
    def get(self, request, format=None):
        return Response('https://gitlab.com/claudiop/KleepAssets/raw/master/Transportation.minimal.svg')


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


class GroupList(APIView):
    def get(self, request, format=None):
        serializer = GroupTypeSerializer(GroupType.objects.all(), many=True)
        return Response(serializer.data)


class Store(APIView):
    def get(self, request, format=None):
        serializer = StoreItemSerializer(StoreItem.objects.all(), many=True)
        return Response(serializer.data)


class NewsList(APIView):
    def get(self, request, format=None):
        serializer = NewsMinimalSerializer(NewsItem.objects.all(), many=True)
        return Response(serializer.data)


class News(APIView):
    def get(self, request, pk, format=None):
        serializer = NewsSerializer(NewsItem.objects.get(id=pk))
        return Response(serializer.data)


class SyopsesAreas(APIView):
    def get(self, request, format=None):
        serializer = SynopsisAreaSerializer(SynopsisArea.objects.all(), many=True)
        return Response(serializer.data)


class SyopsesTopicSections(APIView):
    def get(self, request, pk, format=None):
        serializer = SynopsisTopicSectionsSerializer(SynopsisTopic.objects.get(id=pk))
        return Response(serializer.data)


class Menus(APIView):
    def get(self, request, format=None):
        serializer = BarListMenusSerializer(Bar.objects.all(), many=True)
        return Response(serializer.data)


class ProfileDetailed(APIView):
    def get(self, request, nickname, format=None):  # TODO authentication
        user = Profile.objects.get(nickname=nickname)
        serializer = ProfileDetailedSerializer(user)
        return Response(serializer.data)
