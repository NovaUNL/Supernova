import psutil
from django.contrib.auth import logout, login
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from kleep.forms import LoginForm, AccountCreationForm, AccountSettingsForm, ClipLogin
from kleep.models import Service, Building, User, Group, GroupType, Course, Degree, Department, Class, ClassInstance, \
    TurnInstance, Classroom
from kleep.schedules import build_turns_schedule


def index(request):
    context = __base_context__(request)
    context['title'] = "KLEEarly not a riPoff"  # TODO, change me to something less cringy
    return render(request, 'kleep/index.html', context)


def about(request):
    context = __base_context__(request)
    context['title'] = "Sobre"
    return render(request, 'kleep/about.html', context)


def beg(request):
    context = __base_context__(request)
    context['title'] = "Ajudas"
    return render(request, 'kleep/beg.html', context)


def privacy(request):
    context = __base_context__(request)
    context['title'] = "Politica de privacidade"
    return render(request, 'kleep/privacy.html', context)


def campus(request):
    context = __base_context__(request)
    context['title'] = "Mapa do campus"
    context['buildings'] = Building.objects.all()
    context['services'] = Service.objects.all()
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')}, {'name': 'Mapa', 'url': reverse('campus')}]
    return render(request, 'kleep/campus.html', context)


def campus_transportation(request):
    context = __base_context__(request)
    context['title'] = "Transportes para o campus"
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('campus')},
        {'name': 'Transportes', 'url': reverse('transportation')}]
    return render(request, 'kleep/transportation.html', context)


def profile(request, nickname):
    user = get_object_or_404(User, nickname=nickname)
    context = __base_context__(request)
    page_name = "Perfil de " + user.name
    context['page'] = 'profile'
    context['title'] = page_name
    context['sub_nav'] = [{'name': page_name, 'url': reverse('profile', args=[nickname])}]
    context['rich_user'] = user
    return render(request, 'kleep/profile.html', context)


def profile_schedule(request, nickname):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    context = __base_context__(request)
    user = get_object_or_404(User, id=request.user.id)
    if hasattr(user, 'student'):
        student = user.student
    else:
        return HttpResponseRedirect(reverse('profile', args=[nickname]))
    context['page'] = 'profile_schedule'
    context['title'] = "Horário de " + nickname
    context['sub_nav'] = [{'name': "Perfil de " + user.name, 'url': reverse('profile', args=[nickname])},
                          {'name': "Horário", 'url': reverse('profile_schedule', args=[nickname])}]
    context['weekday_spans'], context['schedule'], context['unsortable'] = build_turns_schedule(student.turn_set.all())
    context['rich_user'] = user
    return render(request, 'kleep/profile_schedule.html', context)


def profile_settings(request, nickname):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    context = __base_context__(request)
    user = User.objects.get(id=request.user.id)
    context['page'] = 'profile_settings'
    context['title'] = "Definições da conta"
    context['sub_nav'] = [{'name': "Perfil de " + user.name, 'url': reverse('profile', args=[nickname])},
                          {'name': "Definições", 'url': reverse('profile_settings', args=[nickname])}]
    context['rich_user'] = user
    if request.method == 'POST':
        form = AccountSettingsForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(reverse('index'))
        else:
            context['settings_form'] = form
    else:
        context['settings_form'] = AccountSettingsForm()

    return render(request, 'kleep/profile_settings.html', context)


def profile_crawler(request, nickname):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    context = __base_context__(request)
    user = User.objects.get(id=request.user.id)
    context['page'] = 'profile_crawler'
    context['title'] = "Definições da conta"
    context['sub_nav'] = [{'name': "Perfil de " + user.name, 'url': reverse('profile', args=[nickname])},
                          {'name': "Agregar CLIP", 'url': reverse('profile_crawler', args=[nickname])}]
    context['rich_user'] = user
    if request.method == 'POST':
        pass
    context['clip_login_form'] = ClipLogin()

    return render(request, 'kleep/profile_crawler.html', context)


def login_view(request):
    context = __base_context__(request)
    context['title'] = "Autenticação"
    context['disable_auth'] = True  # Disable auth overlay

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('profile', args=[request.user]))

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(reverse('index'))
        else:
            print("Invalid")
            context['login_form'] = form
    else:
        context['login_form'] = LoginForm()
    return render(request, 'kleep/login.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def create_account(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('profile', args=[request.user]))

    context = __base_context__(request)
    context['title'] = "Criação de conta"
    if request.method == 'POST':
        pass

    else:
        context['creation_form'] = AccountCreationForm()
    return render(request, 'kleep/create_account.html', context)


def building(request, building_id):
    building = get_object_or_404(Building, id=building_id)
    context = __base_context__(request)
    context['title'] = building.name
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')},
                          {'name': building.name, 'url': reverse('building', args=[building_id])}]
    context['building'] = building
    return render(request, 'kleep/building.html', context)


def service(request, building_id, service_id):
    building = get_object_or_404(Building, id=building_id)
    service = get_object_or_404(Service, id=service_id)
    context = __base_context__(request)
    context['title'] = service.name
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')},
                          {'name': building.name, 'url': reverse('building', args=[building_id])},
                          {'name': service.name, 'url': reverse('service', args=[building_id, service_id])}]
    context['building'] = building
    context['service'] = service
    return render(request, 'kleep/service.html', context)


def groups(request):
    context = __base_context__(request)
    if 'filtro' in request.GET:
        context['type_filter'] = request.GET['filtro']
    context['title'] = "Grupos"
    context['groups'] = Group.objects.all()
    context['group_types'] = GroupType.objects.all()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')}]
    return render(request, 'kleep/groups.html', context)


def group(request, group_id):
    context = __base_context__(request)
    group = get_object_or_404(Group, id=group_id)
    context['title'] = group.name
    context['group'] = group
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group_id])}]
    return render(request, 'kleep/group.html', context)


def departments(request):
    context = __base_context__(request)
    context['title'] = "Departamentos"
    context['departments'] = Department.objects.order_by('name').all()
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')}]
    return render(request, 'kleep/departments.html', context)


def department(request, department_id):
    context = __base_context__(request)
    department = get_object_or_404(Department, id=department_id)
    context['title'] = f'Departamento de {department.name}'
    context['department'] = department
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department.name, 'url': reverse('department', args=[department_id])}]
    return render(request, 'kleep/department.html', context)


def class_view(request, class_id):
    context = __base_context__(request)
    class_ = get_object_or_404(Class, id=class_id)
    department = class_.department
    context['title'] = class_.name
    context['department'] = department
    context['class_obj'] = class_
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department.name, 'url': reverse('department', args=[department.id])},
                          {'name': class_.name, 'url': reverse('class', args=[class_id])}]
    return render(request, 'kleep/class.html', context)


def class_instance_view(request, instance_id):
    context = __base_context__(request)
    instance = get_object_or_404(ClassInstance, id=instance_id)
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
    return render(request, 'kleep/class_instance.html', context)


def class_instance_schedule_view(request, instance_id):
    context = __base_context__(request)
    instance = get_object_or_404(ClassInstance, id=instance_id)
    parent_class = instance.parent
    department = parent_class.department
    context['page'] = 'instance_schedule'
    context['title'] = str(instance)
    context['department'] = department
    context['parent_class'] = parent_class
    context['instance'] = instance
    occasion = instance.occasion()
    context['occasion'] = occasion

    context['weekday_spans'], context['schedule'], context['unsortable'] = build_turns_schedule(instance.turn_set.all())

    context['sub_nav'] = [
        {'name': 'Departamentos', 'url': reverse('departments')},
        {'name': department.name, 'url': reverse('department', args=[department.id])},
        {'name': parent_class.name, 'url': reverse('class', args=[parent_class.id])},
        {'name': occasion, 'url': reverse('class_instance', args=[instance_id])},
        {'name': 'Horário', 'url': request.get_raw_uri()}
    ]
    return render(request, 'kleep/class_instance_schedule.html', context)


def class_instance_turns_view(request, instance_id):
    context = __base_context__(request)
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
    context['turns'] = instance.turn_set.order_by('turn_type', 'number')

    context['sub_nav'] = [
        {'name': 'Departamentos', 'url': reverse('departments')},
        {'name': department.name, 'url': reverse('department', args=[department.id])},
        {'name': parent_class.name, 'url': reverse('class', args=[parent_class.id])},
        {'name': occasion, 'url': reverse('class_instance', args=[instance_id])},
        {'name': 'Horário', 'url': request.get_raw_uri()}
    ]
    return render(request, 'kleep/class_instance_turns.html', context)


def __base_context__(request):
    result = {'cpu': __cpu_load__(),
              'people': 0  # TODO
              }
    if not request.user.is_authenticated:
        result['login_form'] = LoginForm()
    return result


def __cpu_load__():
    cpu_load_val = cache.get('cpu_load')
    if cpu_load_val is None:
        cpu_load_val = psutil.cpu_percent(interval=0.10)  # cache instead of calculating for every request
        cache.set('cpu_load', cpu_load_val, 10)

    if cpu_load_val <= 50.0:
        return 0  # low
    elif cpu_load_val <= 80.0:
        return 1  # medium
    else:
        return 2  # high
