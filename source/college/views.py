from datetime import datetime

from dal import autocomplete
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.vary import vary_on_cookie

import settings
from college.choice_types import Degree, RoomType
from college import models as m
from college import schedules
from college import choice_types as ctypes
from college.utils import get_transportation_departures
from settings import COLLEGE_YEAR, COLLEGE_PERIOD
from supernova.views import build_base_context

from services.models import Service


def index_view(request):
    context = build_base_context(request)
    context['pcode'] = "c"
    context['title'] = "Faculdade"
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')}]
    return render(request, 'college/college.html', context)


def map_view(request):
    context = build_base_context(request)
    context['pcode'] = "c_campus_map"
    context['title'] = "Mapa do campus"
    context['buildings'] = m.Building.objects.all()
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Mapa', 'url': reverse('college:map')}]
    return render(request, 'college/campus.html', context)


def transportation_view(request):
    context = build_base_context(request)
    context['pcode'] = "c_campus_tranportation"
    context['title'] = "Transportes para o campus"
    context['departures'] = get_transportation_departures()
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Transportes', 'url': reverse('college:transportation')}]
    return render(request, 'college/transportation.html', context)


def departments_view(request):
    context = build_base_context(request)
    context['pcode'] = "c_departments"
    context['title'] = "Departamentos"
    context['departments'] = m.Department.objects.order_by('name').filter(extinguished=False).all()
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Departamentos', 'url': reverse('college:departments')}]
    return render(request, 'college/departments.html', context)


def department_view(request, department_id):
    department = get_object_or_404(
        m.Department.objects,
        id=department_id)
    # FIXME this could be a single query instead of 5-6
    degrees = map(
        lambda degree: degree[0],
        m.Course.objects.filter(department=department).order_by('degree').values_list('degree').distinct())
    courses_by_degree = list(
        map(lambda degree:
            (Degree.name(degree), m.Course.objects.filter(department=department, degree=degree).all()),
            degrees))

    context = build_base_context(request)
    context['pcode'] = "c_department"
    context['title'] = f'Departamento de {department.name}'
    context['department'] = department
    context['courses'] = courses_by_degree
    context['classes'] = department.classes.filter(extinguished=False).order_by('name').all()
    # FIXME
    context['teachers'] = department.teachers \
        .filter(shifts__class_instance__year__gt=2015) \
        .distinct().order_by('name')
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department.name, 'url': reverse('college:department', args=[department_id])}]
    return render(request, 'college/department.html', context)


@permission_required('users.full_student_access')
def teacher_view(request, teacher_id):
    teacher = get_object_or_404(m.Teacher, id=teacher_id)
    context = build_base_context(request)
    shifts = teacher.shifts \
        .filter(class_instance__year=settings.COLLEGE_YEAR, class_instance__period=settings.COLLEGE_PERIOD) \
        .exclude(disappeared=True).all()
    context['pcode'] = "c_teachers"
    context['title'] = teacher.name
    context['teacher'] = teacher
    context['class_instances'] = \
        m.ClassInstance.objects \
            .filter(shifts__teachers=teacher) \
            .order_by('parent__name', 'year', 'period') \
            .distinct()
    context['weekday_spans'], context['schedule'], context['unsortable'] = schedules.build_shifts_schedule(shifts)
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Professores', 'url': '#'},
        {'name': teacher.name, 'url': '#'}]
    return render(request, 'college/teacher.html', context)


def _class__nav(klass):
    department_nav = {'name': 'Sem departamento'} if klass.department is None else {
        'name': klass.department.name, 'url': reverse('college:department', args=[klass.department.id])
    }
    return [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        department_nav,
        {'name': klass.name, 'url': reverse('college:class', args=[klass.id])}]


def class_view(request, class_id):
    klass = get_object_or_404(
        m.Class.objects
            .select_related('department')
            .prefetch_related('instances'),
        id=class_id)
    context = build_base_context(request)
    context['pcode'] = "c_class"
    context['title'] = klass.name
    context['klass'] = klass
    context['instances'] = klass.instances.order_by('year', 'period').reverse()
    context['sub_nav'] = _class__nav(klass)
    return render(request, 'college/class.html', context)


def _class_instance_nav(instance):
    department_nav = {'name': 'Sem departamento'} if instance.department is None else {
        'name': instance.department.name, 'url': reverse('college:department', args=[instance.department.id])
    }
    return [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        department_nav,
        {'name': instance.parent.name, 'url': reverse('college:class', args=[instance.parent.id])},
        {'name': instance.occasion, 'url': reverse('college:class_instance', args=[instance.id])}]


@permission_required('users.full_student_access')
def class_instance_view(request, instance_id):
    instance = get_object_or_404(
        m.ClassInstance.objects
            .select_related('parent') \
            .prefetch_related('parent__instances')
            .annotate(enrolled_count=Count('enrollments', distinct=True),
                      course_count=Count('enrollments__student__course', distinct=True)),
        id=instance_id)
    department = instance.department

    context = build_base_context(request)
    context['pcode'] = "c_class_instance"
    context['title'] = str(instance)
    context['department'] = department
    context['instance'] = instance
    context['sub_nav'] = _class_instance_nav(instance)
    return render(request, 'college/class_instance.html', context)


@cache_page(3600 * 24)
@cache_control(max_age=3600 * 24)
@vary_on_cookie
@permission_required('users.full_student_access')
def class_instance_shifts_view(request, instance_id):
    # TODO optimize queries (4 duplicated in the schedule building)
    instance = get_object_or_404(
        m.ClassInstance.objects
            .prefetch_related('shifts__instances__room__building')
            .select_related('parent', 'department'),
        id=instance_id)

    context = build_base_context(request)
    context['pcode'] = "c_class_instance_shifts"
    context['title'] = str(instance)
    context['instance'] = instance
    shifts = instance.shifts \
        .exclude(disappeared=True) \
        .order_by('shift_type', 'number') \
        .prefetch_related('instances__room__building') \
        .all()
    context['weekday_spans'], context['schedule'], context['unsortable'] = schedules.build_shifts_schedule(shifts)
    context['shifts'] = shifts
    sub_nav = _class_instance_nav(instance)
    sub_nav.append({'name': 'Horário', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_shifts.html', context)


@permission_required('users.full_student_access')
def class_instance_enrolled_view(request, instance_id):
    instance = get_object_or_404(
        m.ClassInstance.objects.select_related('parent', 'department'),
        id=instance_id)
    enrollments = instance.enrollments.select_related('student__user').all()
    parent = instance.parent
    department = parent.department

    context = build_base_context(request)
    context['pcode'] = "c_class_instance_enrolled"
    context['title'] = str(instance)
    context['department'] = department
    context['instance'] = instance
    context['enrollments'] = enrollments
    sub_nav = _class_instance_nav(instance)
    sub_nav.append({'name': 'Inscritos', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_enrolled.html', context)


@permission_required('users.full_student_access')
def class_instance_files_view(request, instance_id):
    instance = get_object_or_404(
        m.ClassInstance.objects.select_related('parent', 'department'),
        id=instance_id)
    context = build_base_context(request)

    context['pcode'] = "c_class_instance_files"
    context['title'] = str(instance)
    context['instance'] = instance

    is_enrolled = instance.enrollments.filter(student__user=request.user).exists()
    files = list(instance.files \
                 .select_related('file', 'uploader_teacher') \
                 .order_by('upload_datetime') \
                 .reverse())
    allowed_files = []
    denied_files = []
    suppressed = False
    for file in files:
        if file.license == ctypes.FileAvailability.NOBODY:
            denied_files.append((file, 'nobody'))
        elif file.license == ctypes.FileAvailability.ENROLLED and not is_enrolled:
            denied_files.append((file, 'enrolled'))
        allowed_files.append(file)
    context['suppressed_files'] = suppressed
    context['files'] = allowed_files
    context['denied_files'] = denied_files
    context['instance_files'] = files
    sub_nav = _class_instance_nav(instance)
    sub_nav.append({'name': 'Ficheiros', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_files.html', context)


@permission_required('users.full_student_access')
def class_instance_file_download(request, instance_id, file_hash):
    class_file = get_object_or_404(
        m.ClassFile.objects.prefetch_related('file'),
        class_instance__id=instance_id,
        file__hash=file_hash)
    response = HttpResponse()
    response['Content-Type'] = class_file.file.mime
    if 'inline' not in request.GET:
        response['Content-Disposition'] = f'attachment; filename="{class_file.name}"'

    if class_file.file.external:
        response['X-Accel-Redirect'] = f'/clip/{file_hash[:2]}/{file_hash[2:]}'
    else:
        raise Exception("Not implemented")
    return response


@cache_page(3600 * 24)
@cache_control(max_age=3600 * 24)
@vary_on_cookie
def courses_view(request):
    # FIXME this could be a single query instead of a dozen
    degrees = sorted(map(lambda degree: degree[0],
                         set(m.Course.objects.filter(active=True).values_list('degree'))))
    courses_by_degree = list(
        map(lambda degree:
            (Degree.name(degree),
             m.Course.objects.filter(active=True, degree=degree).all()),
            degrees))

    context = build_base_context(request)
    context['pcode'] = "c_courses"
    context['title'] = "Cursos"
    context['degrees'] = courses_by_degree
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Cursos', 'url': reverse('college:courses')}]
    return render(request, 'college/courses.html', context)


@cache_page(3600 * 24)
@cache_control(max_age=3600 * 24)
@vary_on_cookie
def course_view(request, course_id):
    course = get_object_or_404(m.Course, id=course_id)
    department = course.department
    if department is None:
        department_name = "Desconhecido"
        department_url = "#"
    else:
        department_name = str(department)
        department_url = reverse('college:department', args=[department.id])

    context = build_base_context(request)
    context['pcode'] = "c_course"
    context['title'] = str(course)
    context['course'] = course
    context['student_count'] = course.students.count()
    context['active_student_count'] = course.students.filter(last_year=settings.COLLEGE_YEAR).count()
    context['new_students_count'] = \
        course.students \
            .filter(first_year=settings.COLLEGE_YEAR, last_year=settings.COLLEGE_YEAR) \
            .count()
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department_name, 'url': department_url},
        {'name': course, 'url': reverse('college:course', args=[course_id])}]
    return render(request, 'college/course.html', context)


@cache_page(3600 * 24)
@cache_control(max_age=3600 * 24)
@vary_on_cookie
@permission_required('users.full_student_access')
def course_students_view(request, course_id):
    course = get_object_or_404(m.Course.objects, id=course_id)
    department = course.department
    if department is None:
        department_name = "Desconhecido"
        department_url = "#"
    else:
        department_name = str(department)
        department_url = reverse('college:department', args=[department.id])

    context = build_base_context(request)
    context['pcode'] = "c_courses"
    context['title'] = 'Alunos de %s' % course
    context['course'] = course
    context['students'] = course.students.select_related('user').order_by('number').all()
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department_name, 'url': department_url},
        {'name': course, 'url': reverse('college:course', args=[course_id])},
        {'name': 'Alunos', 'url': reverse('college:course_students', args=[course_id])}]
    return render(request, 'college/course_students.html', context)


def course_curriculum_view(request, course_id):
    course = get_object_or_404(m.Course, id=course_id)
    department = course.department
    curriculum = m.Curriculum.objects.filter(course=course).order_by('year', 'period', 'period_type').all()

    context = build_base_context(request)
    context['pcode'] = "c_course_curriculum"
    context['title'] = 'Programa curricular de %s' % course
    context['course'] = course
    context['curriculum'] = curriculum
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department, 'url': reverse('college:department', args=[department.id])},
        {'name': course, 'url': reverse('college:course', args=[course_id])},
        {'name': 'Programa curricular', 'url': reverse('college:course_curriculum', args=[course_id])}]
    return render(request, 'college/course_curriculum.html', context)


def buildings_view(request):
    context = build_base_context(request)
    context['pcode'] = "c_campus_buildings"
    context['title'] = "Edifícios"
    context['buildings'] = m.Building.objects.order_by('id').all()
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Edifícios', 'url': reverse('college:buildings')}]
    return render(request, 'college/buildings.html', context)


def building_view(request, building_id):
    # TODO This view can probably be optimized
    building = get_object_or_404(
        m.Building.objects.prefetch_related('departments'),
        id=building_id)
    rooms = m.Room.objects.filter(building=building).order_by('type', 'name', 'door_number').all()
    rooms_by_type = {}
    for room in rooms:
        plural = RoomType.plural(room.type)
        if plural not in rooms_by_type:
            rooms_by_type[plural] = []
        rooms_by_type[plural].append(room)
    context = build_base_context(request)
    context['pcode'] = "c_campus_building"
    context['title'] = building.name
    context['rooms'] = sorted(rooms_by_type.items(), key=lambda t: t[0])
    context['services'] = Service.objects.order_by('name').filter(place__building=building)
    context['departments'] = building.departments
    context['room_occupation'] = schedules.build_building_occupation_table(
        COLLEGE_PERIOD, COLLEGE_YEAR, datetime.today().weekday(), building)
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Edifícios', 'url': reverse('college:buildings')},
        {'name': building.name, 'url': reverse('college:building', args=[building_id])}]
    context['building'] = building
    return render(request, 'college/building.html', context)


def room_view(request, room_id):
    room = get_object_or_404(m.Room, id=room_id)
    building = room.building
    shift_instances = room.shift_instances \
        .filter(shift__class_instance__year=COLLEGE_YEAR, shift__class_instance__period=COLLEGE_PERIOD) \
        .exclude(disappeared=True) \
        .all()
    context = build_base_context(request)
    context['pcode'] = "c_campus_building_room"
    context['title'] = str(room)
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': building.name, 'url': reverse('college:building', args=[building.id])},
        {'name': room.name, 'url': reverse('college:room', args=[room_id])}]
    context['building'] = building
    context['room'] = room
    context['weekday_spans'], context['schedule'], context['unsortable'] = schedules.build_schedule(shift_instances)
    return render(request, 'college/room.html', context)


@login_required
def available_places_view(request):
    context = build_base_context(request)
    if not request.user.has_perm('users.full_student_access'):
        context['title'] = context['msg_title'] = 'Insuficiência de permissões'
        context['msg_content'] \
            = 'O seu utilizador não tem permissões suficientes para consultar a informação de espaços.'
        return render(request, 'supernova/message.html', context, status=403)

    context['pcode'] = "c_campus_places"
    context['title'] = 'Espaços disponíveis'
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Espaços disponíveis', 'url': reverse('college:available_places')}]

    date = datetime.now().date()
    context['date'] = date

    if date.isoweekday() >= 5:
        context['weekend'] = True
        return render(request, 'college/available_places.html', context)

    context['weekend'] = False
    context['occupation'] = schedules.build_occupation_table(COLLEGE_PERIOD, COLLEGE_YEAR, datetime.today().weekday())
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Espaços', 'url': reverse('college:available_places')}]
    return render(request, 'college/available_places.html', context)


class ClassAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Class.objects.all()
        if self.q:
            try:
                qs = qs.filter(Q(id=int(self.q)) | Q(name__istartswith=self.q))
            except ValueError:
                qs = qs.filter(title__contains=self.q)
        return qs


class PlaceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Place.objects.all()
        if self.q:
            try:
                qs = qs.filter(Q(id=int(self.q)) | Q(name__istartswith=self.q))
            except ValueError:
                qs = qs.filter(title__contains=self.q)
        return qs
