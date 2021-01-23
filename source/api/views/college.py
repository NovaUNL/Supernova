from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from api.serializers import college as serializers

from college import models as college
from users import models as users
from users.utils import get_students


class BuildingList(APIView):
    def get(self, request):
        serializer = serializers.BuildingSerializer(college.Building.objects.all(), many=True)
        return Response(serializer.data)


class BuildingDetailed(APIView):
    def get(self, request, pk):
        serializer = serializers.BuildingSerializer(college.Building.objects.get(pk=pk))
        return Response(serializer.data)


class DepartmentList(APIView):
    def get(self, request):
        serializer = serializers.DepartmentMinimalSerializer(
            college.Department.objects.all(), many=True)
        return Response(serializer.data)


class DepartmentDetailed(APIView):
    def get(self, request, pk):
        serializer = serializers.DepartmentSerializer(college.Department.objects.get(id=pk))
        return Response(serializer.data)


class CourseDetailed(APIView):
    def get(self, request, pk):
        course = college.Course.objects.get(id=pk)
        data = serializers.CourseSerializer(course).data
        data['degree'] = course.degree.name
        return Response(data)


class ClassDetailed(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        serializer = serializers.CourseSerializer(college.Class.objects.get(id=pk))
        return Response(serializer.data)


class UserShiftInstances(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, nickname):
        user = get_object_or_404(users.User.objects.prefetch_related('students'), nickname=nickname)
        primary_students, _ = get_students(user)

        shift_instances = college.ShiftInstance.objects \
            .select_related('shift__class_instance__parent') \
            .prefetch_related('room__building') \
            .filter(shift__student__in=primary_students,
                    shift__class_instance__year=settings.COLLEGE_YEAR,
                    shift__class_instance__period=settings.COLLEGE_PERIOD) \
            .all()
        serializer = serializers.ScheduleSerializer(shift_instances, many=True)
        return Response(serializer.data)
