from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import college as serializers

from college import models as college


class BuildingList(APIView):
    def get(self, request, format=None):
        serializer = serializers.BuildingSerializer(college.Building.objects.all(), many=True)
        return Response(serializer.data)


class BuildingDetailed(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.BuildingSerializer(college.Building.objects.get(pk=pk))
        return Response(serializer.data)


class DepartmentList(APIView):
    def get(self, request, format=None):
        serializer = serializers.DepartmentMinimalSerializer(
            college.Department.objects.all(), many=True)
        return Response(serializer.data)


class DepartmentDetailed(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.DepartmentSerializer(college.Department.objects.get(id=pk))
        return Response(serializer.data)


class CourseDetailed(APIView):
    def get(self, request, pk, format=None):
        course = college.Course.objects.get(id=pk)
        data = serializers.CourseSerializer(course).data
        data['degree'] = course.degree.name
        return Response(data)


class ClassDetailed(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.CourseSerializer(college.Class.objects.get(id=pk))
        return Response(serializer.data)
