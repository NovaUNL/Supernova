from dal import autocomplete
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from clip import models as clip
from clip.models import Degree
from college.models import Building, Classroom, Laboratory, Auditorium, Place, Course, Curriculum, Area, ClassInstance, \
    Class, Department
from college.schedules import build_schedule, build_turns_schedule
from kleep.settings import COLLEGE_YEAR, COLLEGE_PERIOD
from kleep.views import build_base_context

from services.models import Service, MenuDish


def campus(request):
    context = build_base_context(request)
    context['title'] = "Mapa do campus"
    context['buildings'] = Building.objects.all()
    # context['services'] = Service.objects.all()
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')}, {'name': 'Mapa', 'url': reverse('campus')}]
    return render(request, 'college/campus.html', context)


def transportation(request):
    context = build_base_context(request)
    context['title'] = "Transportes para o campus"
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('campus')},
        {'name': 'Transportes', 'url': reverse('transportation')}]
    return render(request, 'college/transportation.html', context)


def departments(request):
    context = build_base_context(request)
    context['title'] = "Departamentos"
    context['departments'] = Department.objects.order_by('name').filter(extinguished=False).all()
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')}]
    return render(request, 'college/departments.html', context)


def department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    context = build_base_context(request)
    context['title'] = f'Departamento de {department.name}'
    context['department'] = department
    context['degrees'] = Degree.objects.filter(course__department=department).all()
    context['courses'] = Course.objects.filter(department=department).all()
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department.name, 'url': reverse('department', args=[department_id])}]
    return render(request, 'college/department.html', context)


def class_view(request, class_id):
    class_ = get_object_or_404(Class, id=class_id)
    context = build_base_context(request)
    department = class_.department
    context['title'] = class_.name
    context['department'] = department
    context['class_obj'] = class_
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department.name, 'url': reverse('department', args=[department.id])},
                          {'name': class_.name, 'url': reverse('class', args=[class_id])}]
    return render(request, 'college/class.html', context)


def class_instance(request, instance_id):
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
        {'name': 'Departamentos', 'url': reverse('departments')},
        {'name': department.name, 'url': reverse('department', args=[department.id])},
        {'name': parent_class.name, 'url': reverse('class', args=[parent_class.id])},
        {'name': occasion, 'url': reverse('class_instance', args=[instance_id])}
    ]
    return render(request, 'college/class_instance.html', context)


def class_instance_schedule(request, instance_id):
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
        {'name': 'Departamentos', 'url': reverse('departments')},
        {'name': department.name, 'url': reverse('department', args=[department.id])},
        {'name': parent_class.name, 'url': reverse('class', args=[parent_class.id])},
        {'name': occasion, 'url': reverse('class_instance', args=[instance_id])},
        {'name': 'Horário', 'url': request.get_raw_uri()}
    ]
    return render(request, 'college/class_instance_schedule.html', context)


def class_instance_turns(request, instance_id):
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
        {'name': 'Departamentos', 'url': reverse('departments')},
        {'name': department.name, 'url': reverse('department', args=[department.id])},
        {'name': parent_class.name, 'url': reverse('class', args=[parent_class.id])},
        {'name': occasion, 'url': reverse('class_instance', args=[instance_id])},
        {'name': 'Horário', 'url': request.get_raw_uri()}
    ]
    return render(request, 'college/class_instance_turns.html', context)


def areas(request):
    context = build_base_context(request)
    context['title'] = 'Areas de estudo'
    context['areas'] = Area.objects.order_by('name').all()
    context['sub_nav'] = [{'name': 'Areas de estudo', 'url': reverse('areas')}]
    return render(request, 'college/areas.html', context)


def area(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    context = build_base_context(request)
    context['title'] = 'Area de ' + area.name
    context['area'] = area
    context['courses'] = Course.objects.filter(area=area).order_by('degree_id').all()
    context['degrees'] = Degree.objects.filter(course__area=area).all()
    context['sub_nav'] = [{'name': 'Areas de estudo', 'url': reverse('areas')},
                          {'name': area.name, 'url': reverse('area', args=[area_id])}]
    return render(request, 'college/area.html', context)


def course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = build_base_context(request)
    department = course.department
    context['title'] = str(course)

    context['course'] = course
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department, 'url': reverse('department', args=[department.id])},
                          {'name': course, 'url': reverse('course', args=[course_id])}]
    return render(request, 'college/course.html', context)


def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = build_base_context(request)
    department = course.department
    context['title'] = 'Alunos de %s' % course

    context['course'] = course
    context['students'] = course.students.order_by('number').all()
    context['unregistered_students'] = clip.Student.objects.filter(course=course.clip_course, student=None).order_by(
        'internal_id')
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department, 'url': reverse('department', args=[department.id])},
                          {'name': course, 'url': reverse('course', args=[course_id])},
                          {'name': 'Alunos', 'url': reverse('course_students', args=[course_id])}]
    return render(request, 'college/course_students.html', context)


def course_curriculum(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = build_base_context(request)
    department = course.department
    curriculum = Curriculum.objects.filter(course=course).order_by('year', 'period', 'period_type').all()

    context['title'] = 'Programa curricular de %s' % course

    context['course'] = course
    context['curriculum'] = curriculum
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department, 'url': reverse('department', args=[department.id])},
                          {'name': course, 'url': reverse('course', args=[course_id])},
                          {'name': 'Programa curricular', 'url': reverse('course_curriculum', args=[course_id])}]
    return render(request, 'college/course_curriculum.html', context)


def building(request, building_id):
    building = get_object_or_404(Building, id=building_id)
    context = build_base_context(request)
    context['title'] = building.name
    context['classrooms'] = Classroom.objects.order_by('place__name').filter(place__building=building)
    context['laboratories'] = Laboratory.objects.order_by('place__name').filter(place__building=building)
    context['auditoriums'] = Auditorium.objects.order_by('place__name').filter(place__building=building)
    context['services'] = Service.objects.order_by('name').filter(place__building=building)
    context['departments'] = Department.objects.order_by('name').filter(building=building)
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')},
                          {'name': building.name, 'url': reverse('building', args=[building_id])}]
    context['building'] = building
    return render(request, 'college/building.html', context)


def classroom(request, classroom_id):
    classroom = get_object_or_404(Place, id=classroom_id)
    building = classroom.building
    context = build_base_context(request)
    context['title'] = str(classroom)
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')},
                          {'name': building.name, 'url': reverse('building', args=[building.id])},
                          {'name': classroom.name, 'url': reverse('classroom', args=[classroom_id])}]
    context['building'] = building
    context['classroom'] = classroom
    turn_instances = classroom.turn_instances.filter(
        turn__class_instance__year=COLLEGE_YEAR, turn__class_instance__period=COLLEGE_PERIOD).all()
    context['weekday_spans'], context['schedule'], context['unsortable'] = build_schedule(turn_instances)
    return render(request, 'college/classroom.html', context)


def service(request, service_id):
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
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')},
                          {'name': building.name, 'url': reverse('building', args=[building.id])},
                          {'name': service.name, 'url': reverse('service', args=[service_id])}]
    return render(request, 'college/service.html', context)


class ClassAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Class.objects.all()
        if self.q:
            qs = qs.filter(name__startswith=self.q)
        return qs
