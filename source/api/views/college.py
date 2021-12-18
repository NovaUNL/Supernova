from django.shortcuts import get_object_or_404
from django.conf import settings
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


class Building(APIView):
    def get(self, request, building_id):
        building = get_object_or_404(college.Building, id=building_id)
        serializer = serializers.BuildingSerializer(building)
        return Response(serializer.data)


class PlaceList(APIView):
    def get(self, request):
        places = college.Place.objects.select_related('room').all()
        serializer = serializers.PlaceSerializer(places, many=True)
        return Response(serializer.data)


class RoomList(APIView):
    def get(self, request):
        serializer = serializers.SimpleRoomSerializer(college.Room.objects.all(), many=True)
        return Response(serializer.data)


class DepartmentList(APIView):
    def get(self, request):
        serializer = serializers.DepartmentSerializer(college.Department.objects.all(), many=True)
        return Response(serializer.data)


class DepartmentDetailed(APIView):
    def get(self, request, department_id):
        department = get_object_or_404(college.Department, id=department_id)
        serializer = serializers.DepartmentSerializer(department)
        return Response(serializer.data)


# class DepartmentClasses(APIView):
#     def get(self, request, department_id):
#         department = get_object_or_404(college.Department, id=department_id)
#         year_filter = request.GET.get('year')
#         classes = college.Class.objects.filter(department=department).exclude(disappeared=True)
#         if year_filter:
#             classes = classes.filter(instances__year=year_filter).exclude(instances__disappeared=True).distinct()
#         serializer = serializers.ClassSerializer(classes, many=True)
#         return Response(serializer.data)


# class DepartmentClassInstances(APIView):
#     def get(self, request, department_id):
#         year_filter = request.GET.get('year')
#         department = get_object_or_404(college.Department, id=department_id)
#         class_instances = college.ClassInstance.objects.filter(department=department).exclude(disappeared=True)
#         if year_filter:
#             class_instances = class_instances.filter(year=year_filter)
#         serializer = serializers.ClassInstanceMinimalSerializer(class_instances, many=True)
#         return Response(serializer.data)


class ClassList(APIView):
    def get(self, request):
        serializer = serializers.ClassSerializer(
            college.Class.objects.prefetch_related('instances').exclude(disappeared=True)[:2000],
            many=True)
        return Response(serializer.data)


class CoursesList(APIView):
    def get(self, request):
        courses = college.Course.objects.exclude(disappeared=True).all()
        data = serializers.CourseSerializer(courses, many=True).data
        return Response(data)


class CourseDetailed(APIView):
    def get(self, request, course_id):
        course = get_object_or_404(college.Course, id=course_id)
        data = serializers.CourseSerializer(course).data
        return Response(data)


class Class(APIView):
    def get(self, request, class_id):
        klass = get_object_or_404(college.Class, id=class_id)
        serializer = serializers.ClassSerializer(klass)
        return Response(serializer.data)


class UserShiftInstances(APIView):
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


class ClassInstance(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, instance_id):
        instance = get_object_or_404(college.ClassInstance.objects.exclude(disappeared=True), id=instance_id)
        serializer = serializers.ClassInstanceSerializer(instance)
        return Response(serializer.data)


class ClassInstanceShifts(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, instance_id):
        instance = get_object_or_404(college.ClassInstance.objects, id=instance_id)
        shifts = instance.shifts.exclude(disappeared=True)
        serializer = serializers.ShiftSerializer(shifts, many=True)
        return Response(serializer.data)


class ClassFiles(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, instance_id):

        instance = get_object_or_404(
            college.ClassInstance.objects,
            id=instance_id)

        access_override = request.user.is_superuser or False  # <- TODO Verify if the user is the author
        is_enrolled = instance.enrollments.filter(student__user=request.user).exists()
        class_files = list(instance.files \
                           .select_related('file', 'uploader_teacher') \
                           .order_by('upload_datetime') \
                           .reverse())
        official_files = []
        community_files = []
        denied_files = []
        for class_file in class_files:
            if not access_override:
                if class_file.visibility == college.ctypes.FileVisibility.NOBODY:
                    denied_files.append(class_file)
                    continue
                elif class_file.visibility == college.ctypes.FileVisibility.ENROLLED and not is_enrolled:
                    denied_files.append(class_file)
                    continue
            if class_file.official:
                official_files.append(class_file)
            else:
                community_files.append(class_file)
        return Response({
            'official': serializers.ClassFileSerializer(official_files, many=True).data,
            'community': serializers.ClassFileSerializer(community_files, many=True).data,
            'denied': serializers.ClassFileSerializer(denied_files, many=True).data,
        })


class Shift(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, shift_id):
        shift = get_object_or_404(college.Shift.objects, id=shift_id)
        serializer = serializers.ShiftSerializer(shift)
        return Response(serializer.data)


class Enrollment(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, enrollment_id):
        enrollment = get_object_or_404(college.Enrollment.objects, id=enrollment_id)
        serializer = serializers.EnrollmentSerializer(enrollment)
        return Response(serializer.data)


class Student(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, student_id):
        student = get_object_or_404(college.Student.objects.prefetch_related('enrollments'), id=student_id)
        serializer = serializers.StudentSerializer(student)
        return Response(serializer.data)


class Teacher(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, teacher_id):
        teacher = get_object_or_404(college.Teacher.objects.select_related('rank'), id=teacher_id)
        serializer = serializers.TeacherSerializer(teacher)
        return Response(serializer.data)
