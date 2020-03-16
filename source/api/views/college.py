from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

import settings
from api.serializers import college as serializers

from college import models as college
from users import models as users
from users.utils import get_students


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


class UserTurnInstances(APIView):
    def get(self, request, nickname, format=None):
        user = get_object_or_404(users.User.objects.prefetch_related('students'), nickname=nickname)
        primary_students, _ = get_students(user)

        turn_instances = college.TurnInstance.objects \
            .select_related('turn__class_instance__parent') \
            .prefetch_related('room__building') \
            .filter(turn__student__in=primary_students,
                    turn__class_instance__year=settings.COLLEGE_YEAR,
                    turn__class_instance__period=settings.COLLEGE_PERIOD) \
            .annotate(end=F('start') - F('duration')) \
            .all()
        serializer = serializers.ScheduleSerializer(turn_instances, many=True)
        return Response(serializer.data)
