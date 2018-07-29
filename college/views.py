from collections import OrderedDict
from datetime import datetime

from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from clip import models as clip
from college.choice_types import Degree, RoomType
from college.models import Building, Room, Course, Curriculum, Area, ClassInstance, Class, Department, TurnInstance
from college.schedules import build_schedule, build_turns_schedule
from kleep.settings import COLLEGE_YEAR, COLLEGE_PERIOD
from kleep.views import build_base_context

from services.models import Service, MenuDish


def campus_view(request):
    context = build_base_context(request)
    context['title'] = "Mapa do campus"
    context['buildings'] = Building.objects.all()
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Mapa', 'url': reverse('college:map')}]
    return render(request, 'college/campus.html', context)


def map_view(request):
    context = build_base_context(request)
    context['title'] = "Mapa do campus"
    context['buildings'] = Building.objects.all()
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Mapa', 'url': reverse('college:map')}]
    return render(request, 'college/campus.html', context)


def transportation_view(request):
    context = build_base_context(request)
    context['title'] = "Transportes para o campus"
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Transportes', 'url': reverse('college:transportation')}]
    return render(request, 'college/transportation.html', context)


def departments_view(request):
    context = build_base_context(request)
    context['title'] = "Departamentos"
    context['departments'] = Department.objects.order_by('name').filter(extinguished=False).all()
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Departamentos', 'url': reverse('college:departments')}]
    return render(request, 'college/departments.html', context)


def department_view(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    context = build_base_context(request)
    context['title'] = f'Departamento de {department.name}'
    context['department'] = department

    degrees = Course.objects.filter(department=department).values_list('degree').distinct()
    # courses_by_degree = list(
    #     map(lambda degree:
    #         (Degree.name(degree[0]),
    #          Course.objects.filter(department=department, degree=degree[0]).all()),
    #         degrees))
    # context['courses'] = courses_by_degree
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department.name, 'url': reverse('college:department', args=[department_id])}]
    return render(request, 'college/department.html', context)


def class_view(request, class_id):
    class_ = get_object_or_404(Class, id=class_id)
    context = build_base_context(request)
    department = class_.department
    context['title'] = class_.name
    context['department'] = department
    context['class_obj'] = class_
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department.name, 'url': reverse('college:department', args=[department.id])},
        {'name': class_.name, 'url': reverse('college:class', args=[class_id])}]
    return render(request, 'college/class.html', context)


def class_instance_view(request, instance_id):
    instance = get_object_or_404(ClassInstance, id=instance_id)
    context = build_base_context(request)
    parent_class = instance.parent
    department = parent_class.department
    context['page'] = 'instance_index'
    context['title'] = str(instance)
    context['department'] = department
    context['parent_class'] = parent_class
    context['instance'] = instance
    occasion = instance.occasion()
    context['occasion'] = occasion

    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department.name, 'url': reverse('college:department', args=[department.id])},
        {'name': parent_class.name, 'url': reverse('college:class', args=[parent_class.id])},
        {'name': occasion, 'url': reverse('college:class_instance', args=[instance_id])}]
    return render(request, 'college/class_instance.html', context)


def class_instance_schedule_view(request, instance_id):
    instance = get_object_or_404(ClassInstance, id=instance_id)
    context = build_base_context(request)
    parent_class = instance.parent
    department = parent_class.department
    context['page'] = 'instance_schedule'
    context['title'] = str(instance)
    context['department'] = department
    context['parent_class'] = parent_class
    context['instance'] = instance
    occasion = instance.occasion()
    context['occasion'] = occasion

    context['weekday_spans'], context['schedule'], context['unsortable'] = build_turns_schedule(instance.turns.all())

    context['sub_nav'] = [
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department.name, 'url': reverse('college:department', args=[department.id])},
        {'name': parent_class.name, 'url': reverse('college:class', args=[parent_class.id])},
        {'name': occasion, 'url': reverse('college:class_instance', args=[instance_id])},
        {'name': 'Horário', 'url': request.get_raw_uri()}
    ]
    return render(request, 'college/class_instance_schedule.html', context)


def class_instance_turns_view(request, instance_id):
    context = build_base_context(request)
    instance = get_object_or_404(ClassInstance, id=instance_id)
    parent_class = instance.parent
    department = parent_class.department
    context['page'] = 'instance_turns'
    context['title'] = str(instance)
    context['department'] = department
    context['parent_class'] = parent_class
    context['instance'] = instance
    occasion = instance.occasion()
    context['occasion'] = occasion
    context['turns'] = instance.turns.order_by('turn_type', 'number')

    context['sub_nav'] = [
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department.name, 'url': reverse('college:department', args=[department.id])},
        {'name': parent_class.name, 'url': reverse('college:class', args=[parent_class.id])},
        {'name': occasion, 'url': reverse('college:class_instance', args=[instance_id])},
        {'name': 'Horário', 'url': request.get_raw_uri()}
    ]
    return render(request, 'college/class_instance_turns.html', context)


def areas_view(request):
    context = build_base_context(request)
    context['title'] = 'Areas de estudo'
    context['areas'] = Area.objects.order_by('name').all()
    context['sub_nav'] = [{'name': 'Areas de estudo', 'url': reverse('college:areas')}]
    return render(request, 'college/areas.html', context)


def area_view(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    context = build_base_context(request)
    context['title'] = 'Area de ' + area.name
    context['area'] = area
    context['courses'] = Course.objects.filter(area=area).order_by('degree_id').all()
    # context['degrees'] = Degree.objects.filter(course__area=area).all()  # FIXME
    context['sub_nav'] = [{'name': 'Areas de estudo', 'url': reverse('college:areas')},
                          {'name': area.name, 'url': reverse('college:area', args=[area_id])}]
    return render(request, 'college/area.html', context)


def course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = build_base_context(request)
    department = course.department
    context['title'] = str(course)

    context['course'] = course
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department, 'url': reverse('college:department', args=[department.id])},
        {'name': course, 'url': reverse('college:course', args=[course_id])}]
    return render(request, 'college/course.html', context)


@login_required
def course_students_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = build_base_context(request)
    department = course.department
    context['title'] = 'Alunos de %s' % course

    context['course'] = course
    context['students'] = course.students.order_by('number').all()
    context['unregistered_students'] = clip.Student.objects \
        .filter(course=course.clip_course, student=None) \
        .order_by('internal_id')
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department, 'url': reverse('college:department', args=[department.id])},
        {'name': course, 'url': reverse('college:course', args=[course_id])},
        {'name': 'Alunos', 'url': reverse('college:course_students', args=[course_id])}]
    return render(request, 'college/course_students.html', context)


def course_curriculum_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = build_base_context(request)
    department = course.department
    curriculum = Curriculum.objects.filter(course=course).order_by('year', 'period', 'period_type').all()

    context['title'] = 'Programa curricular de %s' % course

    context['course'] = course
    context['curriculum'] = curriculum
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Departamentos', 'url': reverse('college:departments')},
        {'name': department, 'url': reverse('college:department', args=[department.id])},
        {'name': course, 'url': reverse('college:course', args=[course_id])},
        {'name': 'Programa curricular', 'url': reverse('college:course_curriculum', args=[course_id])}]
    return render(request, 'college/course_curriculum.html', context)


def buildings_view(request):
    context = build_base_context(request)
    context['title'] = "Edifícios"
    context['buildings'] = Building.objects.order_by('id').all()
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Edifícios', 'url': reverse('college:buildings')}]
    return render(request, 'college/buildings.html', context)


def building_view(request, building_id):
    building = get_object_or_404(Building, id=building_id)
    context = build_base_context(request)
    context['title'] = building.name
    rooms = Room.objects.filter(building=building).order_by('type', 'name', 'door_number').all()
    rooms_by_type = {}
    for room in rooms:
        plural = RoomType.plural(room.type)
        if plural not in rooms_by_type:
            rooms_by_type[plural] = []
        rooms_by_type[plural].append(room)
    context['rooms'] = sorted(rooms_by_type.items(), key=lambda t: t[0])
    context['services'] = Service.objects.order_by('name').filter(place__building=building)
    context['departments'] = Department.objects.order_by('name').filter(building=building)
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Edifícios', 'url': reverse('college:buildings')},
        {'name': building.name, 'url': reverse('college:building', args=[building_id])}]
    context['building'] = building
    return render(request, 'college/building.html', context)


def room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    building = room.building
    context = build_base_context(request)
    context['title'] = str(room)
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': building.name, 'url': reverse('college:building', args=[building.id])},
        {'name': room.name, 'url': reverse('college:room', args=[room_id])}]
    context['building'] = building
    context['room'] = room
    turn_instances = room.turn_instances \
        .filter(turn__class_instance__year=COLLEGE_YEAR, turn__class_instance__period=COLLEGE_PERIOD).all()
    context['weekday_spans'], context['schedule'], context['unsortable'] = build_schedule(turn_instances)
    return render(request, 'college/room.html', context)


def service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    building = service.place.building
    context = build_base_context(request)
    context['title'] = service.name
    is_bar = hasattr(service, 'bar')
    context['is_bar'] = is_bar
    if is_bar:
        menu = []
        # TODO today filter
        for menu_item in MenuDish.objects.filter(service=service).all():
            price = menu_item.price
            if price > 0:
                menu.append((menu_item.item, menu_item.price_str()))
            else:
                menu.append((menu_item.item, None))
        context['menu'] = menu
    context['building'] = building
    context['service'] = service
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': building.name, 'url': reverse('college:building', args=[building.id])},
        {'name': service.name, 'url': reverse('college:service', args=[service_id])}]
    return render(request, 'college/service.html', context)


def available_places_view(request):
    context = build_base_context(request)
    context['title'] = 'Espaços disponíveis'
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Espaços disponíveis', 'url': reverse('college:available_places')}]

    date = datetime.now().date()
    context['date'] = date

    if date.isoweekday() > 7:
        context['weekend'] = True
        return render(request, 'college/available_places.html', context)

    context['weekend'] = False
    building_turns = []
    for building in Building.objects.order_by('id').all():
        rooms = []
        for room in Room.objects.filter(building=building).all():
            time_slots = []
            time = 8 * 60  # Start at 8 AM
            empty_state = False if room.type == RoomType.CLASSROOM or room.unlocked else None
            for turn in TurnInstance.objects.filter(room=room, weekday=0,
                                                    turn__class_instance__period=COLLEGE_PERIOD,
                                                    turn__class_instance__year=COLLEGE_YEAR).order_by('start').all():
                if turn.start < time:
                    if turn.start + turn.duration > time:
                        busy_slots = int((turn.start - time + turn.duration) / 30)
                        time = turn.start + turn.duration
                    else:
                        continue
                else:
                    empty_slots = int((turn.start - time) / 30)
                    busy_slots = int(turn.duration / 30)
                    time = turn.start + turn.duration

                    for _ in range(empty_slots):
                        time_slots.append(empty_state)  # False stands for empty
                if time > 20 * 60:  # Past 8PM, remove additional slots
                    busy_slots -= int((time - (20 * 60)) / 30)
                for _ in range(busy_slots):
                    time_slots.append(True)  # True stands for busy
            for _ in range(time, 20 * 60, 30):
                time_slots.append(empty_state)
            rooms.append((room, time_slots))
        if len(rooms) > 0:
            building_turns.append((building, rooms))

    context['turns'] = building_turns

    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('college:campus')},
        {'name': 'Espaços', 'url': reverse('college:available_places')}]
    return render(request, 'college/available_places.html', context)


class ClassAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Class.objects.all()
        if self.q:
            qs = qs.filter(name__startswith=self.q)
        return qs
