from rest_framework.response import Response
from rest_framework.views import APIView

from api import serializers
from college import models as college
from groups import models as groups
from news import models as news
from store import models as store
from services import models as services
from users import models as users
from synopses import models as synopses


class BuildingList(APIView):
    def get(self, request, format=None):
        serializer = serializers.college.BuildingSerializer(college.Building.objects.all(), many=True)
        return Response(serializer.data)


class BuildingDetailed(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.college.BuildingSerializer(college.Building.objects.get(pk=pk))
        return Response(serializer.data)


class CampusMap(APIView):
    def get(self, request, format=None):
        serializer = serializers.college.BuildingSerializer(college.Building.objects.all(), many=True)
        return Response({'map_url': 'https://gitlab.com/claudiop/KleepAssets/raw/master/Campus.svg',
                         'buildings': serializer.data})


class ServiceList(APIView):
    def get(self, request, format=None):
        serializer = serializers.services.ServiceWithBuildingSerializer(
            college.Service.objects.filter(bar__isnull=True).all(), many=True)
        return Response(serializer.data)


class BarList(APIView):
    def get(self, request, format=None):
        serializer = serializers.services.ServiceWithBuildingSerializer(
            college.Service.objects.filter(bar__isnull=False).all(), many=True)
        return Response(serializer.data)


class DepartmentList(APIView):
    def get(self, request, format=None):
        serializer = serializers.college.DepartmentMinimalSerializer(
            college.Department.objects.all(), many=True)
        return Response(serializer.data)


class DepartmentDetailed(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.college.DepartmentSerializer(college.Department.objects.get(id=pk))
        return Response(serializer.data)


class CourseDetailed(APIView):
    def get(self, request, pk, format=None):
        course = college.Course.objects.get(id=pk)
        data = serializers.college.CourseSerializer(course).data
        data['degree'] = course.degree.name
        return Response(data)


class ClassDetailed(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.college.CourseSerializer(college.Class.objects.get(id=pk))
        return Response(serializer.data)


class GroupList(APIView):
    def get(self, request, format=None):
        serializer = serializers.groups.GroupTypeSerializer(groups.Type.objects.all(), many=True)
        return Response(serializer.data)


class Store(APIView):
    def get(self, request, format=None):
        serializer = serializers.services.StoreItemSerializer(store.Item.objects.all(), many=True)
        return Response(serializer.data)


class NewsList(APIView):
    def get(self, request, format=None):
        serializer = serializers.news.NewsMinimalSerializer(news.NewsItem.objects.all(), many=True)
        return Response(serializer.data)


class News(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.news.NewsSerializer(news.NewsItem.objects.get(id=pk))
        return Response(serializer.data)


class SyopsesAreas(APIView):
    def get(self, request, format=None):
        serializer = serializers.synopses.AreaSerializer(synopses.Area.objects.all(), many=True)
        return Response(serializer.data)


class SyopsesTopicSections(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.synopses.TopicSectionsSerializer(synopses.Topic.objects.get(id=pk))
        return Response(serializer.data)


class Menus(APIView):
    def get(self, request, format=None):
        serializer = serializers.services.BarListMenusSerializer(
            services.Service.objects.filter(restaurant=True).all(), many=True)
        return Response(serializer.data)


class ProfileDetailed(APIView):
    def get(self, request, nickname, format=None):  # TODO authentication
        user = users.User.objects.get(nickname=nickname)
        serializer = serializers.users.ProfileDetailedSerializer(user)
        return Response(serializer.data)
