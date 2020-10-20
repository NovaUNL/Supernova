from datetime import datetime, timedelta
from functools import reduce

from dal import autocomplete
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.vary import vary_on_cookie

import settings
from college.choice_types import Degree, RoomType
from college import models as m
from college import forms as f
from college import schedules
from college import choice_types as ctypes
from college.utils import get_transportation_departures, get_file_name_parts, prettify_file_name
from feedback.forms import ReviewForm
from feedback import models as feedback
from settings import COLLEGE_YEAR, COLLEGE_PERIOD
from supernova.storage import HashedFilenameFileSystemStorage
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


@login_required
@permission_required('college.change_department', raise_exception=True)
def department_edit_view(request, department_id):
    department = get_object_or_404(
        m.Department.objects,
        id=department_id)

    if request.method == 'POST':
        form = f.DepartmentForm(request.POST, request.FILES, instance=department)
        if form.is_valid():
            if form.has_changed():
                changes = form.get_changes()
                margin = timezone.now() - timedelta(minutes=5)
                last_edit = m.AcademicDataChange.objects \
                    .filter(department=department, timestamp__gt=margin) \
                    .order_by('timestamp') \
                    .reverse() \
                    .first()
                with transaction.atomic():
                    if last_edit is None or last_edit.user != request.user:
                        m.AcademicDataChange.objects.create(
                            user=request.user,
                            changed_object=department,
                            changes=changes)
                    else:
                        last_edit.changes = f.merge_changes(last_edit.changes, changes)
                        last_edit.save(update_fields=['changes'])
                    form.save()
            return redirect('college:department', department_id=department_id)
    else:
        form = f.DepartmentForm(instance=department)

    context = build_base_context(request)
    context['pcode'] = "c_department"
    context['title'] = f'Departamento de {department.name}'
    context['department'] = department
    context['form'] = form
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department.name, 'url': reverse('college:department', args=[department_id])},
        {'name': 'Editar', 'url': reverse('college:department_edit', args=[department_id])}]
    return render(request, 'college/department_edit.html', context)


@login_required
@permission_required('users.student_access')
def teacher_view(request, teacher_id):
    teacher = get_object_or_404(m.Teacher.objects.select_related('rank'), id=teacher_id)
    context = build_base_context(request)
    shifts = teacher.shifts \
        .filter(class_instance__year=settings.COLLEGE_YEAR, class_instance__period=settings.COLLEGE_PERIOD) \
        .select_related('class_instance__parent') \
        .exclude(disappeared=True).all()
    context['pcode'] = "c_teachers"
    context['title'] = teacher.name
    context['teacher'] = teacher
    context['class_instances'] = \
        m.ClassInstance.objects \
            .filter(shifts__teachers=teacher) \
            .order_by('parent__name', 'year', 'period') \
            .select_related('parent') \
            .distinct()
    context['reviews'] = teacher.reviews.all()
    context['weekday_spans'], context['schedule'], context['unsortable'] = schedules.build_shifts_schedule(shifts)
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Professores', 'url': '#'},
        {'name': teacher.name, 'url': reverse('college:teacher', args=[teacher_id])}]
    return render(request, 'college/teacher.html', context)


@login_required
@permission_required('college.change_teacher', raise_exception=True)
def teacher_edit_view(request, teacher_id):
    teacher = get_object_or_404(m.Teacher, id=teacher_id)

    if request.method == 'POST':
        form = f.TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            if form.has_changed():
                changes = form.get_changes()
                margin = timezone.now() - timedelta(minutes=10)
                last_edit = m.AcademicDataChange.objects \
                    .filter(teacher=teacher, timestamp__gt=margin) \
                    .order_by('timestamp') \
                    .reverse() \
                    .first()
                with transaction.atomic():
                    if last_edit is None or last_edit.user != request.user:
                        m.AcademicDataChange.objects.create(
                            user=request.user,
                            changed_object=teacher,
                            changes=changes)
                    else:
                        last_edit.changes = f.merge_changes(last_edit.changes, changes)
                        last_edit.save(update_fields=['changes'])
                    form.save()
            return redirect('college:teacher', teacher_id=teacher_id)
    else:
        form = f.TeacherForm(instance=teacher)

    context = build_base_context(request)
    context['pcode'] = "c_teachers"
    context['title'] = teacher.name
    context['teacher'] = teacher
    context['form'] = form
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Professores'},
        {'name': teacher.name, 'url': reverse('college:teacher', args=[teacher_id])},
        {'name': 'Editar', 'url': '#'}]
    return render(request, 'college/teacher_edit.html', context)


@login_required
@permission_required('users.student_access')
def teacher_reviews_view(request, teacher_id):
    teacher = get_object_or_404(m.Teacher.objects, id=teacher_id)
    context = build_base_context(request)
    context['title'] = f"Avaliações de {teacher.name}"
    context['pcode'] = "c_teachers"
    context['reviews'] = teacher.reviews.all()
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Professores', 'url': '#'},
        {'name': teacher.name, 'url': reverse('college:teacher', args=[teacher_id])},
        {'name': 'Avaliações', 'url': request.get_raw_uri()}]
    return render(request, 'feedback/reviews.html', context)


@login_required
@permission_required('users.student_access')
def teacher_review_create_view(request, teacher_id):
    teacher = get_object_or_404(m.Teacher.objects, id=teacher_id)

    context = build_base_context(request)
    context['title'] = f"Nova avaliação a {teacher.name}"
    context['pcode'] = "c_teachers"
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.object_id = teacher_id
            review.content_type = ContentType.objects.get_for_model(m.Teacher)
            review.save()
            return redirect('college:teacher_reviews', teacher_id=teacher_id)
    else:
        form = ReviewForm()
    context['form'] = form
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Professores', 'url': '#'},
        {'name': teacher.name, 'url': reverse('college:teacher', args=[teacher_id])},
        {'name': 'Avaliar', 'url': request.get_raw_uri()},
    ]
    return render(request, 'feedback/review_create.html', context)


def _class__nav(klass):
    department_nav = {'name': 'Sem departamento'} if klass.department is None else {
        'name': klass.department.name, 'url': reverse('college:department', args=[klass.department.id])
    }
    return [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        department_nav,
        {'name': klass.name, 'url': reverse('college:class', args=[klass.id])}]


@cache_page(3600)
@cache_control(private=True, max_age=3600)
@vary_on_cookie
@login_required
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
    context['reviews'] = feedback.Review.objects.filter(class_instance__parent=klass).all()
    context['teachers'] = m.Teacher.objects \
        .filter(shifts__class_instance__parent=klass) \
        .order_by('name') \
        .distinct('name')
    context['sub_nav'] = _class__nav(klass)
    return render(request, 'college/class.html', context)


def class_edit_view(request, class_id):
    klass = get_object_or_404(m.Class.objects, id=class_id)

    if request.method == 'POST':
        form = f.ClassForm(request.POST, request.FILES, instance=klass)
        if form.is_valid():
            if form.has_changed():
                changes = form.get_changes()
                margin = timezone.now() - timedelta(minutes=5)
                last_edit = m.AcademicDataChange.objects \
                    .filter(klass=klass, timestamp__gt=margin) \
                    .order_by('timestamp') \
                    .reverse() \
                    .first()
                with transaction.atomic():
                    if last_edit is None or last_edit.user != request.user:
                        m.AcademicDataChange.objects.create(
                            user=request.user,
                            changed_object=klass,
                            changes=changes)
                    else:
                        last_edit.changes = f.merge_changes(last_edit.changes, changes)
                        last_edit.save(update_fields=['changes'])
                    form.save()
            return redirect('college:class', class_id=class_id)
    else:
        form = f.ClassForm(instance=klass)

    context = build_base_context(request)
    context['pcode'] = "c_class"
    context['title'] = klass.name
    context['klass'] = klass
    context['form'] = form
    sub_nav = _class__nav(klass)
    sub_nav.append({'name': 'Editar', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_edit.html', context)


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


@cache_page(3600)
@cache_control(private=True, max_age=3600)
@vary_on_cookie
@login_required
@permission_required('users.student_access')
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
    context['reviews'] = instance.reviews.all()
    context['teachers'] = m.Teacher.objects.filter(shifts__class_instance=instance).order_by('name').distinct('name')
    context['sub_nav'] = _class_instance_nav(instance)
    return render(request, 'college/class_instance.html', context)


@login_required
@permission_required('college.classinstance_change', raise_exception=True)
def class_instance_edit_view(request, instance_id):
    instance = get_object_or_404(m.ClassInstance.objects.select_related('parent'), id=instance_id)

    if request.method == 'POST':
        form = f.ClassInstanceForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            if form.has_changed():
                changes = form.get_changes()
                margin = timezone.now() - timedelta(minutes=5)
                last_edit = m.AcademicDataChange.objects \
                    .filter(class_instance=instance, timestamp__gt=margin) \
                    .order_by('timestamp') \
                    .reverse() \
                    .first()
                with transaction.atomic():
                    if last_edit is None or last_edit.user != request.user:
                        m.AcademicDataChange.objects.create(
                            user=request.user,
                            changed_object=instance,
                            changes=changes)
                    else:
                        last_edit.changes = f.merge_changes(last_edit.changes, changes)
                        last_edit.save(update_fields=['changes'])
                    form.save()
            return redirect('college:class_instance', instance_id=instance_id)
    else:
        form = f.ClassInstanceForm(instance=instance)

    context = build_base_context(request)
    context['pcode'] = "c_class_instance_edit"
    context['title'] = str(instance)
    context['instance'] = instance
    context['form'] = form
    sub_nav = _class_instance_nav(instance)
    sub_nav.append({'name': 'Editar', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_edit.html', context)


@cache_page(3600)
@cache_control(max_age=3600)
@vary_on_cookie
@permission_required('users.student_access')
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
    sub_nav.append({'name': 'Turnos', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_shifts.html', context)


@cache_page(3600 * 24)
@cache_control(max_age=3600 * 24)
@vary_on_cookie
@login_required
@permission_required('users.student_access')
def class_instance_enrolled_view(request, instance_id):
    instance = get_object_or_404(
        m.ClassInstance.objects.select_related('parent', 'department'),
        id=instance_id)
    parent = instance.parent
    department = parent.department
    enrollments = m.Enrollment.objects \
        .filter(class_instance=instance) \
        .order_by('student__number') \
        .select_related('student__course', 'student__user') \
        .all()

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


@cache_page(3600)
@cache_control(max_age=3600)
@vary_on_cookie
@login_required
@permission_required('users.student_access')
def class_instance_events_view(request, instance_id):
    instance = get_object_or_404(
        m.ClassInstance.objects.select_related('parent', 'department'),
        id=instance_id)
    parent = instance.parent
    department = parent.department

    context = build_base_context(request)
    context['pcode'] = "c_class_instance_enrolled"
    context['title'] = str(instance)
    events = m.ClassInstanceEvent.objects \
        .filter(class_instance=instance) \
        .select_related('class_instance__parent')
    context['evaluations'] = next_evaluations \
        = list(filter(lambda e: e.type in (ctypes.EventType.TEST, ctypes.EventType.EXAM), events))
    context['events'] = list(filter(lambda e: e not in next_evaluations, events))

    context['department'] = department
    context['instance'] = instance
    sub_nav = _class_instance_nav(instance)
    sub_nav.append({'name': 'Eventos', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_events.html', context)


@login_required
@permission_required('users.student_access')
def class_instance_files_view(request, instance_id):
    instance = get_object_or_404(
        m.ClassInstance.objects.select_related('parent', 'department'),
        id=instance_id)
    context = build_base_context(request)

    context['pcode'] = "c_class_instance_files"
    context['title'] = str(instance)
    context['instance'] = instance

    access_override = request.user.is_superuser or False  # <- TODO Verify if one is the author
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
            if class_file.visibility == ctypes.FileVisibility.NOBODY:
                denied_files.append((class_file, 'nobody'))
                continue
            elif class_file.visibility == ctypes.FileVisibility.ENROLLED and not is_enrolled:
                denied_files.append((class_file, 'enrolled'))
                continue
        if class_file.official:
            official_files.append(class_file)
        else:
            community_files.append(class_file)
    context['official_files'] = official_files
    context['community_files'] = community_files
    context['denied_files'] = denied_files
    context['instance_files'] = class_files
    sub_nav = _class_instance_nav(instance)
    sub_nav.append({'name': 'Ficheiros', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_files.html', context)


@login_required
@permission_required('users.student_access')
def class_instance_file_view(request, instance_id, class_file_id):
    class_file = get_object_or_404(
        m.ClassFile.objects.select_related('file', 'class_instance__parent__department'),
        id=class_file_id,
        class_instance_id=instance_id)
    class_instance = class_file.class_instance
    context = build_base_context(request)
    context['pcode'] = "c_class_instance_file"
    context['title'] = f'Ficheiro {class_file}'
    context['instance'] = class_instance
    context['class_file'] = class_file
    context['file'] = class_file.file
    context['other_class_instances'] = m.ClassInstance.objects \
        .filter(files__file__hash=class_file.file.hash) \
        .exclude(id=instance_id) \
        .all()
    sub_nav = _class_instance_nav(class_instance)
    sub_nav.append({'name': 'Ficheiros', 'url': reverse('college:class_instance_files', args=[class_instance.id])})
    sub_nav.append({'name': class_file.name, 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_file.html', context)


@login_required
@permission_required('users.student_access')
def class_instance_file_download(request, instance_id, file_hash):
    class_file = get_object_or_404(
        m.ClassFile.objects.prefetch_related('file'),
        class_instance__id=instance_id,
        file__hash=file_hash)

    permission = False

    # Is staff or teacher?
    if request.user.is_staff or request.user.is_teacher:
        permission = True

    # Is this file public in any of its instances?
    if not permission:
        if request.user.is_student:
            public_groups = (m.ctypes.FileVisibility.PUBLIC, m.ctypes.FileVisibility.STUDENTS)
        else:
            public_groups = (m.ctypes.FileVisibility.PUBLIC,)
        permission = class_file.visibility in public_groups

    # Is this file_instance enrollment-public?
    if not permission and class_file.visibility == m.ctypes.FileVisibility.ENROLLED:
        permission = m.ClassFile.objects \
            .filter(file=class_file,
                    class_instance__student__user=request.user) \
            .exists()

    if not permission:
        return HttpResponseForbidden()

    response = HttpResponse()
    response['Content-Type'] = class_file.file.mime
    response['X-Frame-Options'] = 'SAMEORIGIN'

    if 'inline' not in request.GET:
        response['Content-Disposition'] = f'attachment; filename="{class_file.name}"'

    if class_file.file.external:
        response['X-Accel-Redirect'] = f'{settings.EXTERNAL_URL}/{file_hash[:2]}/{file_hash[2:]}'
    else:
        response['X-Accel-Redirect'] = f'{settings.PROTECTED_URL}/{file_hash[:2]}/{file_hash[2:]}'
    return response


@login_required
@permission_required('users.student_access')
def file_download(request, file_hash):
    file = get_object_or_404(
        m.File.objects.prefetch_related('file'),
        hash=file_hash)
    permission = False

    # Is staff or teacher?
    if request.user.is_staff or request.user.is_teacher:
        permission = True

    # Is this file public in any of its instances?
    if not permission:
        if request.user.is_student:
            public_groups = (m.ctypes.FileVisibility.PUBLIC, m.ctypes.FileVisibility.STUDENTS)
        else:
            public_groups = (m.ctypes.FileVisibility.PUBLIC,)
        permission = m.ClassFile.objects \
            .filter(file=file, visibility__in=public_groups) \
            .exists()

    # Is this student enrolled to any instance with enrollment-public?
    if not permission:
        permission = m.ClassFile.objects \
            .filter(file=file,
                    class_instance__student__user=request.user,
                    visibility=m.ctypes.FileVisibility.ENROLLED) \
            .exists()

    if not permission:
        return HttpResponseForbidden()

    # Permission granted, carry on
    response = HttpResponse()
    response['Content-Type'] = file.mime
    response['X-Frame-Options'] = 'SAMEORIGIN'
    if 'inline' not in request.GET:
        response['Content-Disposition'] = f'attachment; filename="{file.hash}"'

    if file.external:
        response['X-Accel-Redirect'] = f'{settings.EXTERNAL_URL}/{file_hash[:2]}/{file_hash[2:]}'
    else:
        response['X-Accel-Redirect'] = f'{settings.PROTECTED_URL}/{file_hash[:2]}/{file_hash[2:]}'
    return response


@login_required
@permission_required('users.teacher_access')
def class_instance_files_edit_view(request, instance_id):
    instance = get_object_or_404(m.ClassInstance.objects, id=instance_id)
    context = build_base_context(request)
    context['pcode'] = "c_class_file"
    context['title'] = f'Edição dos ficheiros de {instance}'
    context['instance'] = instance
    context['formset'] = f.ClassFileFormset(instance=instance, queryset=instance.files.filter(disappeared=False))
    sub_nav = _class_instance_nav(instance)
    sub_nav.append({'name': 'Ficheiros', 'url': reverse('college:class_instance_files', args=[instance.id])})
    sub_nav.append({'name': 'Editar', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_files_edit.html', context)


@login_required
@permission_required('users.teacher_access')
def class_instance_file_attach_view(request, instance_id, file_hash=None):
    instance = get_object_or_404(m.ClassInstance.objects, id=instance_id)
    context = build_base_context(request)
    referenced_file = None
    if file_hash:
        context['file'] = referenced_file = m.File.objects.filter(hash=file_hash).first()

    if request.method == 'POST':
        form = f.ClassFileForm(request.POST) if referenced_file else f.ClassFileCompleteForm(request.POST)

        if form.is_valid():
            class_file = form.save(commit=False)
            if referenced_file:
                class_file.file = referenced_file
            class_file.uploader = request.user
            class_file.class_instance = instance
            user_is_teacher = m.ClassInstance.objects \
                .filter(id=instance.id, shifts__teachers__user=request.user) \
                .exists()
            class_file.official = user_is_teacher
            class_file.save()
    else:
        if referenced_file:
            form = f.ClassFileForm(
                initial={'name': prettify_file_name(context['file'].name),
                         'visibility': m.ctypes.FileVisibility.PUBLIC})
        else:
            form = f.ClassFileCompleteForm(initial={'visibility': m.ctypes.FileVisibility.PUBLIC})

    context['pcode'] = "c_class_files_upload"
    context['title'] = f'Anexar ficheiro a {instance}'
    context['instance'] = instance
    context['form'] = form
    sub_nav = _class_instance_nav(instance)
    sub_nav.append({'name': 'Ficheiros', 'url': reverse('college:class_instance_files', args=[instance.id])})
    sub_nav.append({'name': 'Editar',
                    'url': reverse('college:class_instance_files_edit', args=[instance.id])})
    sub_nav.append({'name': 'Anexar', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_file_attach.html', context)


@login_required
@permission_required('users.teacher_access')
def class_instance_file_edit_view(request, instance_id, class_file_id):
    class_file = get_object_or_404(
        m.ClassFile.objects.select_related('class_instance__parent__department'),
        id=class_file_id,
        class_instance=instance_id)

    if request.method == 'POST':
        form = f.ClassFileForm(request.POST, request.FILES, instance=class_file)
        if form.is_valid():
            if form.has_changed():
                changes = form.get_changes()
                margin = timezone.now() - timedelta(minutes=5)
                last_edit = m.AcademicDataChange.objects \
                    .filter(class_file=class_file, timestamp__gt=margin) \
                    .order_by('timestamp') \
                    .reverse() \
                    .first()
                with transaction.atomic():
                    if last_edit is None or last_edit.user != request.user:
                        m.AcademicDataChange.objects.create(
                            user=request.user,
                            changed_object=class_file,
                            changes=changes)
                    else:
                        last_edit.changes = f.merge_changes(last_edit.changes, changes)
                        last_edit.save(update_fields=['changes'])
                    form.save()
    else:
        form = f.ClassFileForm(instance=class_file)

    context = build_base_context(request)
    context['pcode'] = "c_class_file"
    context['title'] = f'Edição de {class_file}'
    context['instance'] = class_file.class_instance
    context['form'] = form
    sub_nav = _class_instance_nav(class_file.class_instance)
    sub_nav.append({'name': 'Ficheiros',
                    'url': reverse('college:class_instance_files', args=[class_file.class_instance.id])})
    sub_nav.append({'name': 'Editar',
                    'url': reverse('college:class_instance_files_edit', args=[class_file.class_instance.id])})
    sub_nav.append({'name': class_file.name, 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/class_instance_file_edit.html', context)


@login_required
@permission_required('users.student_access')
def class_instance_reviews_view(request, instance_id):
    instance = get_object_or_404(m.ClassInstance.objects.select_related('parent'), id=instance_id)

    context = build_base_context(request)
    context['title'] = f"Avaliações de {instance}"
    context['pcode'] = "c_class_instance_evaluations"
    context['reviews'] = instance.reviews.all()
    sub_nav = _class_instance_nav(instance)
    sub_nav.append({'name': 'Avaliações', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'feedback/reviews.html', context)


@login_required
@permission_required('users.student_access')
def class_instance_review_create_view(request, instance_id):
    instance = get_object_or_404(m.ClassInstance.objects.select_related('parent'), id=instance_id)
    context = build_base_context(request)

    context['title'] = f"Nova avaliação a {instance}"
    context['pcode'] = "c_class_instance_evaluations"
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.object_id = instance_id
            review.content_type = ContentType.objects.get_for_model(m.ClassInstance)
            review.save()
            return redirect('college:class_instance_reviews', instance_id=instance_id)
    else:
        form = ReviewForm()
    context['form'] = form
    sub_nav = _class_instance_nav(instance)
    sub_nav.append({'name': 'Ficheiros', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'feedback/review_create.html', context)


@login_required
@permission_required('users.student_access')
def file_view(request, file_hash):
    file = get_object_or_404(m.File.objects, hash=file_hash)
    context = build_base_context(request)
    context['pcode'] = "c_file"
    context['title'] = f'Ficheiro {file_hash}'
    context['file'] = file
    context['class_files'] = m.ClassFile.objects \
        .select_related('class_instance') \
        .filter(file__hash=file.hash) \
        .all()
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Ficheiros', 'url': reverse('college:campus')},
        {'name': file.hash_tag, 'url': reverse('college:file', args=[file_hash])}]
    return render(request, 'college/file.html', context)


@login_required
@permission_required('users.teacher_access')
def file_edit_view(request, file_hash):
    file = get_object_or_404(m.File.objects, hash=file_hash)

    if request.method == 'POST':
        form = f.FileForm(request.POST, request.FILES, instance=file)
        if form.is_valid():
            if form.has_changed():
                changes = form.get_changes()
                margin = timezone.now() - timedelta(minutes=5)
                last_edit = m.AcademicDataChange.objects \
                    .filter(file=file, timestamp__gt=margin) \
                    .order_by('timestamp') \
                    .reverse() \
                    .first()
                with transaction.atomic():
                    if last_edit is None or last_edit.user != request.user:
                        m.AcademicDataChange.objects.create(
                            user=request.user,
                            changed_object=file,
                            changes=changes)
                    else:
                        last_edit.changes = f.merge_changes(last_edit.changes, changes)
                        last_edit.save(update_fields=['changes'])
                    form.save()
    else:
        form = f.FileForm(instance=file)

    context = build_base_context(request)
    context['pcode'] = "c_file"
    context['title'] = f'Edição do ficheiro {file_hash}'
    context['file'] = file
    context['duplicated'] = 'dupl' in request.GET
    context['form'] = form
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Ficheiros', 'url': reverse('college:campus')},
        {'name': file.hash[:8], 'url': reverse('college:file', args=[file_hash])},
        {'name': 'Editar', 'url': reverse('college:file_edit', args=[file_hash])}]
    return render(request, 'college/file_edit.html', context)


file_storage = HashedFilenameFileSystemStorage(location=settings.PROTECTED_ROOT)


@login_required
@permission_required('users.teacher_access')
def file_upload_view(request):
    context = build_base_context(request)
    class_instance = None
    if 'i' in request.GET:
        try:
            context['class_instance'] = class_instance = get_object_or_404(
                m.ClassInstance.objects.select_related('parent'),
                id=int(request.GET['i']))
        except:
            pass

    if request.method == 'POST':
        form = f.FileUploadForm(request.POST, request.FILES, initial={'author': request.user})
        if form.is_valid():
            new_file = form.cleaned_data['file']
            _, new_file_hash = file_storage.save(None, new_file)
            existing = m.File.objects.filter(hash=new_file).first()
            if existing:
                return redirect(reverse('college:file_edit', args=[new_file_hash]) + "?dupl=")

            file = form.save(commit=False)
            file.name, file.extension = get_file_name_parts(new_file.name)
            file.size = new_file.size
            file.hash = new_file_hash
            file.mime = new_file.content_type
            file.uploader = request.user
            file.external = False
            file.save()
            if class_instance:
                return redirect(
                    'college:class_instance_new_file_attach',
                    instance_id=class_instance.id,
                    file_hash=file.hash)
            else:
                return redirect('college:file_edit', file_hash=new_file_hash)
    else:
        form = f.FileUploadForm(initial={'authors': [request.user]})

    context['pcode'] = "c_file_upload"
    context['title'] = f'Novo ficheiro'
    context['form'] = form
    if True:
        sub_nav = _class_instance_nav(class_instance)
        sub_nav.append({'name': 'Ficheiros', 'url': reverse('college:class_instance_files', args=[class_instance.id])})
        sub_nav.append({'name': 'Editar',
                        'url': reverse('college:class_instance_files_edit', args=[class_instance.id])})
        sub_nav.append({'name': 'Novo', 'url': request.get_raw_uri()})
        context['sub_nav'] = sub_nav
    return render(request, 'college/file_upload.html', context)


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


def _course__nav(course):
    department_nav = {'name': 'Sem departamento'} if course.department is None else {
        'name': course.department.name, 'url': reverse('college:department', args=[course.department.id])
    }
    return [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        department_nav,
        {'name': str(course), 'url': reverse('college:course', args=[course.id])}]


@cache_page(3600 * 24)
@cache_control(max_age=3600 * 24)
@vary_on_cookie
def course_view(request, course_id):
    course = get_object_or_404(
        m.Course.objects.select_related('department', 'coordinator'),
        id=course_id)

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
    context['sub_nav'] = _course__nav(course)
    return render(request, 'college/course.html', context)


@login_required
@permission_required('course.change_course', raise_exception=True)
def course_edit_view(request, course_id):
    course = get_object_or_404(
        m.Course.objects.select_related('department', 'coordinator'),
        id=course_id)

    if request.method == 'POST':
        form = f.CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            if form.has_changed():
                changes = form.get_changes()
                margin = timezone.now() - timedelta(minutes=5)
                last_edit = m.AcademicDataChange.objects \
                    .filter(course=course, timestamp__gt=margin) \
                    .order_by('timestamp') \
                    .reverse() \
                    .first()
                with transaction.atomic():
                    if last_edit is None or last_edit.user != request.user:
                        m.AcademicDataChange.objects.create(
                            user=request.user,
                            changed_object=course,
                            changes=changes)
                    else:
                        last_edit.changes = f.merge_changes(last_edit.changes, changes)
                        last_edit.save(update_fields=['changes'])
                    form.save()
            return redirect('college:course', course_id=course_id)
    else:
        form = f.CourseForm(instance=course)

    context = build_base_context(request)
    context['pcode'] = "c_course"
    context['title'] = str(course)
    context['course'] = course
    context['form'] = form
    sub_nav = _course__nav(course)
    sub_nav.append({'name': 'Editar', 'url': request.get_raw_uri()})
    context['sub_nav'] = sub_nav
    return render(request, 'college/course_edit.html', context)


@cache_page(3600 * 24)
@cache_control(max_age=3600 * 24)
@vary_on_cookie
@permission_required('users.student_access')
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
    room = get_object_or_404(m.Room.objects.select_related('building'), id=room_id)
    building = room.building
    shift_instances = room.shift_instances \
        .filter(shift__class_instance__year=COLLEGE_YEAR, shift__class_instance__period=COLLEGE_PERIOD) \
        .exclude(disappeared=True) \
        .all()
    context = build_base_context(request)
    context['pcode'] = "c_campus_building_room"
    context['title'] = str(room)
    context['building'] = building
    context['room'] = room
    context['weekday_spans'], context['schedule'], context['unsortable'] = schedules.build_schedule(shift_instances)
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': building.name, 'url': reverse('college:building', args=[building.id])},
        {'name': room.name, 'url': reverse('college:room', args=[room_id])}]
    return render(request, 'college/room.html', context)


@permission_required('college.add_room')
def room_create_view(request, building_id):
    building = get_object_or_404(m.Building, id=building_id)
    if request.method == 'POST':
        form = f.RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.building = building
            room.save()
            return redirect('college:room', room_id=room.id)
    else:
        form = f.RoomForm()
    context = build_base_context(request)
    context['pcode'] = "c_campus_building_room"
    context['title'] = f"Criar sala em {building}"
    context['building'] = building
    context['form'] = form
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': building.name, 'url': reverse('college:building', args=[building.id])},
        {'name': 'Criar sala', 'url': request.get_raw_uri()}]
    return render(request, 'college/room_edit.html', context)


@permission_required('college.change_room')
def room_edit_view(request, room_id):
    room = get_object_or_404(m.Room.objects.select_related('building'), id=room_id)
    if request.method == 'POST':
        form = f.RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save()
            return redirect('college:room', room_id=room.id)
    else:
        form = f.RoomForm(instance=room)
    building = room.building
    context = build_base_context(request)
    context['pcode'] = "c_campus_building_room"
    context['title'] = str(room)
    context['building'] = building
    context['room'] = room
    context['form'] = form
    context['sub_nav'] = [
        {'name': 'Faculdade', 'url': reverse('college:index')},
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': building.name, 'url': reverse('college:building', args=[building.id])},
        {'name': room.name, 'url': reverse('college:room', args=[room_id])},
        {'name': 'Editar', 'url': request.get_raw_uri()}]
    return render(request, 'college/room_edit.html', context)


@login_required
def available_places_view(request):
    context = build_base_context(request)
    if not request.user.has_perm('users.student_access'):
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


@login_required
def teacher_consent_view(request):
    context = build_base_context(request)
    context['pcode'] = "c_teacher_consent"
    context['title'] = 'Consentimento docente'
    context['teachers'] = m.Teacher.objects.order_by('name').all()
    return render(request, 'college/teacher_consent.html', context)


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


class TeacherAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Teacher.objects.all()
        if self.q and len(self.q) >= 5:
            filter = reduce(lambda x, y: x & y, [Q(name__icontains=word) for word in self.q.split(' ')])
            qs = qs.filter(filter)
            return qs
        return []


class UnregisteredTeacherAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Teacher.objects.all()
        if self.q and len(self.q) >= 5:
            filter = reduce(lambda x, y: x & y, [Q(name__icontains=word) for word in self.q.split(' ')])
            qs = qs.filter(filter, user=None)
            return qs
        return []


class StudentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if self.q and len(self.q) >= 5:
            qs = m.Student.objects
            filter = Q(abbreviation__icontains=self.q)
            try:
                filter = filter | Q(number=int(self.q))
            except ValueError:
                pass
            qs = qs.filter(filter)
            return qs
        return []


class UnregisteredStudentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if self.q and len(self.q) >= 5:
            qs = m.Student.objects
            filter = Q(abbreviation__icontains=self.q)
            try:
                filter = filter | Q(number=int(self.q))
            except ValueError:
                pass
            qs = qs.filter(filter, user=None)
            return qs
        return []


class FileAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.File.objects.all()
        if self.q:
            qs = qs.filter(hash__istartswith=self.q)
        return qs
