import random
import psutil
from django.contrib.auth import logout, login
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.timezone import now

from kleep.forms import LoginForm, AccountCreationForm, AccountSettingsForm, ClipLoginForm, CreateSynopsisSectionForm
from kleep.models import Service, Building, Profile, Group, GroupType, Department, Class, ClassInstance, Place, \
    NewsItem, Area, Course, Curriculum, Event, PartyEvent, WorkshopEvent, \
    SynopsisArea, SynopsisTopic, SynopsisSection, SynopsisSectionTopic, Article, StoreItem, ChangeLog, BarDailyMenu, \
    Catchphrase, Document, GroupExternalConversation, GroupAnnouncement, Degree, ClipStudent, SynopsisSubarea, \
    SynopsisSectionLog, ClassSynopses, ClassSynopsesSections
from kleep.schedules import build_turns_schedule, build_schedule
from kleep.settings import VERSION


def index(request):
    context = __base_context__(request)
    context['title'] = "O sistema que não deixa folhas soltas"
    context['news'] = NewsItem.objects.order_by('datetime').reverse()[0:5]
    context['changelog'] = ChangeLog.objects.order_by('date').reverse()[0:3]
    context['catchphrase'] = random.choice(Catchphrase.objects.all())
    return render(request, 'kleep/index.html', context)


def about(request):
    context = __base_context__(request)
    context['title'] = "Sobre"
    context['version'] = VERSION
    print(VERSION)
    return render(request, 'kleep/standalone/about.html', context)


def beg(request):
    context = __base_context__(request)
    context['title'] = "Ajudas"
    return render(request, 'kleep/standalone/beg.html', context)


def privacy(request):
    context = __base_context__(request)
    context['title'] = "Politica de privacidade"
    return render(request, 'kleep/standalone/privacy.html', context)


def campus(request):
    context = __base_context__(request)
    context['title'] = "Mapa do campus"
    context['buildings'] = Building.objects.all()
    context['services'] = Service.objects.all()
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')}, {'name': 'Mapa', 'url': reverse('campus')}]
    return render(request, 'kleep/campus/campus.html', context)


def campus_transportation(request):
    context = __base_context__(request)
    context['title'] = "Transportes para o campus"
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('campus')},
        {'name': 'Transportes', 'url': reverse('transportation')}]
    return render(request, 'kleep/campus/transportation.html', context)


def profile(request, nickname):
    profile = get_object_or_404(Profile, nickname=nickname)
    context = __base_context__(request)
    page_name = "Perfil de " + profile.name
    context['page'] = 'profile'
    context['title'] = page_name
    context['sub_nav'] = [{'name': page_name, 'url': reverse('profile', args=[nickname])}]
    context['rich_user'] = profile
    return render(request, 'kleep/profile/profile.html', context)


def profile_schedule(request, nickname):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    context = __base_context__(request)
    user = get_object_or_404(Profile, id=request.user.id)

    if user.student_set.exists():
        student = user.student_set.first()  # FIXME
    else:
        return HttpResponseRedirect(reverse('profile', args=[nickname]))
    context['page'] = 'profile_schedule'
    context['title'] = "Horário de " + nickname
    context['sub_nav'] = [{'name': "Perfil de " + user.name, 'url': reverse('profile', args=[nickname])},
                          {'name': "Horário", 'url': reverse('profile_schedule', args=[nickname])}]
    context['weekday_spans'], context['schedule'], context['unsortable'] = build_turns_schedule(student.turn_set.all())
    context['rich_user'] = user
    return render(request, 'kleep/profile/profile_schedule.html', context)


def profile_settings(request, nickname):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    context = __base_context__(request)
    user = Profile.objects.get(id=request.user.id)
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

    return render(request, 'kleep/profile/profile_settings.html', context)


def profile_crawler(request, nickname):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    context = __base_context__(request)
    profile = request.user.profile
    context['page'] = 'profile_crawler'
    context['title'] = "Definições da conta"
    context['sub_nav'] = [{'name': "Perfil de " + profile.name, 'url': reverse('profile', args=[nickname])},
                          {'name': "Agregar CLIP", 'url': reverse('profile_crawler', args=[nickname])}]
    context['profile'] = profile
    if request.method == 'POST':
        pass
    context['clip_login_form'] = ClipLoginForm()

    return render(request, 'kleep/profile/profile_crawler.html', context)


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
    return render(request, 'kleep/profile/login.html', context)


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
    return render(request, 'kleep/profile/create_account.html', context)


def building(request, building_id):
    building = get_object_or_404(Building, id=building_id)
    context = __base_context__(request)
    context['title'] = building.name
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')},
                          {'name': building.name, 'url': reverse('building', args=[building_id])}]
    context['building'] = building
    return render(request, 'kleep/campus/building.html', context)


def classroom_view(request, classroom_id):
    classroom = get_object_or_404(Place, id=classroom_id)
    building = classroom.building
    context = __base_context__(request)
    context['title'] = str(classroom)
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')},
                          {'name': building.name, 'url': reverse('building', args=[building.id])},
                          {'name': classroom.name, 'url': reverse('classroom', args=[classroom_id])}]
    context['building'] = building
    context['classroom'] = classroom
    turn_instances = classroom.turninstance_set.filter(  # TODO create function to return current school year/period
        turn__class_instance__year=2018, turn__class_instance__period=2).all()
    context['weekday_spans'], context['schedule'], context['unsortable'] = build_schedule(turn_instances)
    return render(request, 'kleep/campus/classroom.html', context)


def service(request, building_id, service_id):
    building = get_object_or_404(Building, id=building_id)
    service = get_object_or_404(Service, id=service_id)
    context = __base_context__(request)
    context['title'] = service.name
    is_bar = hasattr(service, 'bar')
    context['is_bar'] = is_bar
    if is_bar:
        menu = []
        # TODO today filter
        for menu_item in BarDailyMenu.objects.filter(bar=service.bar).order_by('date').all():
            price = menu_item.price
            if price > 0:
                menu.append((menu_item.item, menu_item.price_str()))
            else:
                menu.append((menu_item.item, None))
        context['menu'] = menu
    context['building'] = building
    context['service'] = service
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')},
                          {'name': building.name, 'url': reverse('building', args=[building_id])},
                          {'name': service.name, 'url': reverse('service', args=[building_id, service_id])}]
    return render(request, 'kleep/campus/service.html', context)


def groups(request):
    context = __base_context__(request)
    if 'filtro' in request.GET:
        context['type_filter'] = request.GET['filtro']
    context['title'] = "Grupos"
    context['groups'] = Group.objects.all()
    context['group_types'] = None
    # a = GroupType.objects.all()
    # a[0].type
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')}]
    return render(request, 'kleep/group/groups.html', context)


def group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    context = __base_context__(request)
    context['title'] = group.name
    context['group'] = group
    context['page'] = 'group'
    context['announcements'] = GroupAnnouncement.objects.filter(group=group).order_by('datetime').reverse()[0:5]
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group_id])}]
    return render(request, 'kleep/group/group.html', context)


def group_announcements(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    context = __base_context__(request)
    context['title'] = f'Anúncios de {group.name}'
    context['group'] = group
    context['page'] = 'group_anouncements'
    context['announcements'] = GroupAnnouncement.objects.filter(group=group).order_by('datetime').reverse()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group_id])},
                          {'name': 'Anúncios', 'url': reverse('group_announcement', args=[group_id])}]
    return render(request, 'kleep/group/announcements.html', context)


def group_announcement(request, announcement_id):
    announcement = get_object_or_404(GroupAnnouncement, id=announcement_id)
    group = announcement.group
    context = __base_context__(request)
    context['title'] = announcement.title
    context['group'] = group
    context['announcement'] = announcement
    context['page'] = 'group_anouncement'
    context['announcements'] = GroupAnnouncement.objects.filter(group=group).order_by('datetime').reverse()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group.id])},
                          {'name': 'Anúncios', 'url': reverse('group_announcements', args=[group.id])},
                          {'name': announcement.title, 'url': reverse('group_announcements', args=[group.id])}]
    return render(request, 'kleep/group/announcement.html', context)


def group_documents(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    context = __base_context__(request)
    context['title'] = f'Documentos de {group.name}'
    context['group'] = group
    context['page'] = 'group_documents'
    context['documents'] = Document.objects.filter(author_group=group).all()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group_id])},
                          {'name': 'Documentos', 'url': reverse('group_documents', args=[group_id])}]
    return render(request, 'kleep/group/documents.html', context)


def group_contact(request, group_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    group = get_object_or_404(Group, id=group_id)
    context = __base_context__(request)
    context['title'] = f'Contactar {group.name}'
    context['group'] = group
    context['page'] = 'group_contact'
    context['conversations'] = GroupExternalConversation.objects.filter(
        group=group, creator=request.user.profile).order_by('date').reverse()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group_id])},
                          {'name': 'Contactar', 'url': reverse('group_contact', args=[group_id])}]
    return render(request, 'kleep/group/conversations.html', context)


def document(request, document_id):
    context = __base_context__(request)
    document = get_object_or_404(Document, id=document_id)
    title = document.title
    context['title'] = title
    context['document'] = document
    context['sub_nav'] = [{'name': 'Documentos', 'url': '#'},
                          {'name': title, 'url': '#'}]
    return render(request, 'kleep/standalone/document.html', context)


def departments(request):
    context = __base_context__(request)
    context['title'] = "Departamentos"
    context['departments'] = Department.objects.order_by('name').all()
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')}]
    return render(request, 'kleep/academic/departments.html', context)


def department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    context = __base_context__(request)
    context['title'] = f'Departamento de {department.name}'
    context['department'] = department
    context['degrees'] = Degree.objects.filter(course__department=department).all()
    context['courses'] = Course.objects.filter(department=department).all()
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department.name, 'url': reverse('department', args=[department_id])}]
    return render(request, 'kleep/academic/department.html', context)


def class_view(request, class_id):
    class_ = get_object_or_404(Class, id=class_id)
    context = __base_context__(request)
    department = class_.department
    context['title'] = class_.name
    context['department'] = department
    context['class_obj'] = class_
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department.name, 'url': reverse('department', args=[department.id])},
                          {'name': class_.name, 'url': reverse('class', args=[class_id])}]
    return render(request, 'kleep/academic/class.html', context)


def class_instance_view(request, instance_id):
    instance = get_object_or_404(ClassInstance, id=instance_id)
    context = __base_context__(request)
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
    return render(request, 'kleep/academic/class_instance.html', context)


def class_instance_schedule_view(request, instance_id):
    instance = get_object_or_404(ClassInstance, id=instance_id)
    context = __base_context__(request)
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
    return render(request, 'kleep/academic/class_instance_schedule.html', context)


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
    return render(request, 'kleep/academic/class_instance_turns.html', context)


def areas(request):
    context = __base_context__(request)
    context['title'] = 'Areas de estudo'
    context['areas'] = Area.objects.order_by('name').all()
    context['sub_nav'] = [{'name': 'Areas de estudo', 'url': reverse('areas')}]
    return render(request, 'kleep/academic/areas.html', context)


def area(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    context = __base_context__(request)
    context['title'] = 'Area de ' + area.name
    context['area'] = area
    context['courses'] = Course.objects.filter(area=area).order_by('degree_id').all()
    context['degrees'] = Degree.objects.filter(course__area=area).all()
    context['sub_nav'] = [{'name': 'Areas de estudo', 'url': reverse('areas')},
                          {'name': area.name, 'url': reverse('area', args=[area_id])}]
    return render(request, 'kleep/academic/area.html', context)


def course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = __base_context__(request)
    department = course.department
    context['title'] = str(course)

    context['course'] = course
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department, 'url': reverse('department', args=[department.id])},
                          {'name': course, 'url': reverse('course', args=[course_id])}]
    return render(request, 'kleep/academic/course.html', context)


def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = __base_context__(request)
    department = course.department
    context['title'] = 'Alunos de %s' % course

    context['course'] = course
    context['students'] = course.student_set.order_by('studentcourse__last_year', 'number').all()
    context['unregistered_students'] = ClipStudent.objects.filter(
        course=course.clip_course, student=None).order_by('internal_id')
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department, 'url': reverse('department', args=[department.id])},
                          {'name': course, 'url': reverse('course', args=[course_id])},
                          {'name': 'Alunos', 'url': reverse('course_students', args=[course_id])}]
    return render(request, 'kleep/academic/course_students.html', context)


def course_curriculum(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    context = __base_context__(request)
    department = course.department
    curriculum = Curriculum.objects.filter(course=course).order_by('year', 'period', 'period_type').all()

    context['title'] = 'Programa curricular de %s' % course

    context['course'] = course
    context['curriculum'] = curriculum
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department, 'url': reverse('department', args=[department.id])},
                          {'name': course, 'url': reverse('course', args=[course_id])},
                          {'name': 'Programa curricular', 'url': reverse('course_curriculum', args=[course_id])}]
    return render(request, 'kleep/academic/course_curriculum.html', context)


def news(request):
    context = __base_context__(request)
    context['title'] = 'Notícias'
    context['news'] = NewsItem.objects.order_by('datetime').reverse()[0:10]
    context['sub_nav'] = [{'name': 'Noticias', 'url': reverse('news')}]
    return render(request, 'kleep/news/news.html', context)


def news_item(request, news_item_id):
    context = __base_context__(request)
    news_item = get_object_or_404(NewsItem, id=news_item_id)
    context['page'] = 'instance_turns'
    context['title'] = 'Notícia:' + news_item.title
    context['news_item'] = news_item
    context['sub_nav'] = [{'name': 'Noticias', 'url': reverse('news')},
                          {'name': news_item.title, 'url': reverse('news_item', args=[news_item_id])}]
    return render(request, 'kleep/news/news_item.html', context)


def events(request):
    context = __base_context__(request)
    context['page'] = 'instance_turns'
    context['title'] = 'Eventos'
    context['events'] = Event.objects.filter(  # Only events starting from now, and excluding turn events
        start_datetime__gt=now(), turnevent__isnull=True).order_by('announce_date').reverse()[0:10]
    context['next_workshops'] = WorkshopEvent.objects.order_by('start_datetime')[0:10]
    context['next_parties'] = PartyEvent.objects.order_by('start_datetime')[0:10]
    context['sub_nav'] = [{'name': 'Eventos', 'url': reverse('events')}]
    return render(request, 'kleep/events/events.html', context)


def event(request, event_id):
    context = __base_context__(request)
    context['title'] = 'Evento '  # TODO
    context['page'] = 'instance_turns'
    event = get_object_or_404(Event, id=event_id)
    if hasattr(event, 'workshop'):
        return HttpResponseRedirect('index')  # TODO
    else:
        pass


def synopsis_areas(request):
    context = __base_context__(request)
    context['title'] = 'Resumos - Areas de estudo'
    context['areas'] = SynopsisArea.objects.all()
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopsis_areas')}]
    return render(request, 'kleep/synopses/areas.html', context)


def synopsis_area(request, area_id):
    area = get_object_or_404(SynopsisArea, id=area_id)
    context = __base_context__(request)
    context['title'] = 'Resumos - Categorias de %s' % area.name
    context['area'] = area
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopsis_areas')},
                          {'name': area.name, 'url': reverse('synopsis_area', args=[area_id])}]
    return render(request, 'kleep/synopses/area.html', context)


def synopsis_subarea(request, subarea_id):
    subarea = get_object_or_404(SynopsisSubarea, id=subarea_id)
    area = subarea.area
    context = __base_context__(request)
    context['title'] = 'Resumos - %s (%s)' % (subarea.name, area.name)
    context['subarea'] = subarea
    context['area'] = area
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopsis_areas')},
                          {'name': area.name, 'url': reverse('synopsis_area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopsis_subarea', args=[subarea_id])}]
    return render(request, 'kleep/synopses/subarea.html', context)


def synopsis_topic(request, topic_id):
    context = __base_context__(request)
    topic = get_object_or_404(SynopsisTopic, id=topic_id)
    subarea = topic.sub_area
    area = subarea.area
    context['title'] = topic.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['sections'] = topic.sections.order_by('synopsissectiontopic__index').all()
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopsis_areas')},
                          {'name': area.name, 'url': reverse('synopsis_area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopsis_subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopsis_topic', args=[topic_id])}]
    return render(request, 'kleep/synopses/topic.html', context)


def synopsis_section(request, topic_id, section_id):
    context = __base_context__(request)
    topic = get_object_or_404(SynopsisTopic, id=topic_id)
    section = get_object_or_404(SynopsisSection, id=section_id)
    if section not in topic.sections.all():
        return HttpResponseRedirect(reverse('synopsis_topic', args=[topic_id]))
    subarea = topic.sub_area
    area = subarea.area
    context['title'] = topic.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['section'] = section
    section_topic_relation = SynopsisSectionTopic.objects.filter(topic=topic, section=section).first()
    prev_section = SynopsisSectionTopic.objects.filter(
        topic=topic, index__lt=section_topic_relation.index).order_by('index').last()
    next_section = SynopsisSectionTopic.objects.filter(
        topic=topic, index__gt=section_topic_relation.index).order_by('index').first()
    if prev_section:
        context['previous_section'] = prev_section.section
    if next_section:
        context['next_section'] = next_section.section
    context['authors'] = section.synopsissectionlog_set.distinct('author')
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopsis_areas')},
                          {'name': area.name, 'url': reverse('synopsis_area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopsis_subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopsis_topic', args=[topic_id])},
                          {'name': section.name, 'url': reverse('synopsis_section', args=[topic_id, section_id])}]
    return render(request, 'kleep/synopses/section.html', context)


def synopsis_create_section(request, topic_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    topic = get_object_or_404(SynopsisTopic, id=topic_id)
    context = __base_context__(request)
    choices = [(0, 'Início')] + list(map(lambda section: (section.id, section.name),
                                         SynopsisSection.objects.filter(synopsistopic=topic_id)
                                         .order_by('synopsissectiontopic__index').all()))
    if request.method == 'POST':
        form = CreateSynopsisSectionForm(data=request.POST)
        form.fields['after'].choices = choices
        if form.is_valid():
            if form.fields['after'] == 0:
                index = 1
            else:
                # TODO validate
                index = SynopsisSectionTopic.objects.get(topic=topic, section_id=form.cleaned_data['after']).index + 1

            for entry in SynopsisSectionTopic.objects.filter(topic=topic, index__gte=index).all():
                entry.index += 1
                entry.save()

            section = SynopsisSection(name=form.cleaned_data['name'], content=form.cleaned_data['content'])
            section.save()
            section_topic_rel = SynopsisSectionTopic(topic=topic, section=section, index=index)
            section_topic_rel.save()
            section_log = SynopsisSectionLog(author=request.user, section=section)
            section_log.save()
            return HttpResponseRedirect(reverse('synopsis_section', args=[topic_id, section.id]))
    else:
        form = CreateSynopsisSectionForm()
        form.fields['after'].choices = choices

    subarea = topic.sub_area
    area = subarea.area
    context['title'] = 'Criar nova entrada em %s' % topic.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['form'] = form

    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopsis_areas')},
                          {'name': area.name, 'url': reverse('synopsis_area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopsis_subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopsis_topic', args=[topic_id])},
                          {'name': 'Criar entrada', 'url': reverse('synopsis_create_section', args=[topic_id])}]
    return render(request, 'kleep/synopses/generic_form.html', context)


def synopsis_edit_section(request, topic_id, section_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    topic = get_object_or_404(SynopsisTopic, id=topic_id)
    section = get_object_or_404(SynopsisSection, id=section_id)
    if not SynopsisSectionTopic.objects.filter(section=section, topic=topic).exists():
        return HttpResponseRedirect(reverse('synopsis_topic', args=[topic_id]))
    section_topic_rel = SynopsisSectionTopic.objects.get(section=section, topic=topic)
    context = __base_context__(request)
    choices = [(0, 'Início')]
    for other_section in SynopsisSection.objects.filter(synopsistopic=topic).order_by(
            'synopsissectiontopic__index').all():
        if other_section == section:
            continue
        choices += ((other_section.id, other_section.name),)

    if request.method == 'POST':
        form = CreateSynopsisSectionForm(data=request.POST)
        form.fields['after'].choices = choices
        if form.is_valid():
            if form.fields['after'] == 0:
                index = 1
            else:
                index = SynopsisSectionTopic.objects.get(topic=topic, section_id=form.cleaned_data['after']).index + 1

            if SynopsisSectionTopic.objects.filter(topic=topic, index=index).exclude(section=section).exists():
                for entry in SynopsisSectionTopic.objects.filter(topic=topic, index__gte=index).all():
                    entry.index += 1
                    entry.save()

            section.name = form.cleaned_data['name']
            if section.content != form.cleaned_data['content']:
                log = SynopsisSectionLog(author=request.user, section=section, previous_content=section.content)
                section.content = form.cleaned_data['content']
                log.save()
            section.save()

            section_topic_rel.index = index
            section_topic_rel.save()
            return HttpResponseRedirect(reverse('synopsis_section', args=[topic_id, section.id]))
    else:
        prev_topic_section = SynopsisSectionTopic.objects.filter(
            topic=topic, index__lt=section_topic_rel.index).order_by('index').last()
        if prev_topic_section:
            prev_section_id = prev_topic_section.section.id
        else:
            prev_section_id = 0
        form = CreateSynopsisSectionForm(
            initial={'name': section.name, 'content': section.content, 'after': prev_section_id})
        form.fields['after'].choices = choices

    subarea = topic.sub_area
    area = subarea.area
    context['title'] = 'Editar %s' % section.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['form'] = form

    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopsis_areas')},
                          {'name': area.name, 'url': reverse('synopsis_area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopsis_subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopsis_topic', args=[topic_id])},
                          {'name': section.name, 'url': reverse('synopsis_section', args=[topic_id, section_id])},
                          {'name': 'Editar', 'url': reverse('synopsis_edit_section', args=[topic_id, section_id])}]
    return render(request, 'kleep/synopses/generic_form.html', context)


def class_synopsis(request, class_id):
    class_ = get_object_or_404(Class, id=class_id)
    count = ClassSynopses.objects.filter(corresponding_class=class_).count()
    synopsis = ClassSynopses.objects.get(corresponding_class=class_) if count == 1 else None
    sections = ClassSynopsesSections.objects.order_by('index').filter(class_synopsis=synopsis).all()
    context = __base_context__(request)
    department = class_.department
    context['title'] = 'Resumo de %s' % class_.name
    context['department'] = department
    context['class_obj'] = class_
    context['synopsis'] = synopsis
    context['msg'] = sections.count()
    context['sections'] = sections
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department.name, 'url': reverse('department', args=[department.id])},
                          {'name': class_.name, 'url': reverse('class', args=[class_id])},
                          {'name': 'Resumo', 'url': reverse('class_synopsis', args=[class_id])}]
    return render(request, 'kleep/synopses/class.html', context)


def class_synopsis_section(request, class_id, section_id):
    class_ = get_object_or_404(Class, id=class_id)
    section = get_object_or_404(SynopsisSection, id=section_id)

    class_synopsis_section = ClassSynopsesSections.objects.get(section=section,
                                                               class_synopsis__corresponding_class=class_)
    related_sections = ClassSynopsesSections.objects \
        .filter(class_synopsis__corresponding_class=class_).order_by('index')
    previous_section = related_sections.filter(index__lt=class_synopsis_section.index).last()
    next_section = related_sections.filter(index__gt=class_synopsis_section.index).first()

    context = __base_context__(request)
    department = class_.department
    context['title'] = '%s (%s)' % (class_synopsis_section.section.name, class_.name)
    context['department'] = department
    context['class_obj'] = class_
    context['section'] = class_synopsis_section.section
    context['previous_section'] = previous_section
    context['next_section'] = next_section
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department.name, 'url': reverse('department', args=[department.id])},
                          {'name': class_.name, 'url': reverse('class', args=[class_id])},
                          {'name': 'Resumo', 'url': reverse('class_synopsis', args=[class_id])}]
    return render(request, 'kleep/synopses/class_section.html', context)


def articles(request):
    context = __base_context__(request)
    context['title'] = 'Artigos'
    context['articles'] = Article.objects.order_by('datetime').reverse()[0:10]
    context['sub_nav'] = [{'name': 'Artigos', 'url': reverse('articles')}]
    return render(request, 'kleep/TODO.html', context)


def article_item(request, article_id):
    context = __base_context__(request)
    article = get_object_or_404(Article, id=article_id)
    context['title'] = article.name
    context['articles'] = Article.objects.order_by('datetime').reverse()[0:10]
    context['sub_nav'] = [{'name': 'Artigos', 'url': reverse('articles')},
                          {'name': article.name, 'url': reverse('article_item', args=[article_id])}]
    return render(request, 'kleep/TODO.html', context)


def lunch(request):
    context = __base_context__(request)
    context['title'] = 'Menus'
    context['sub_nav'] = [{'name': 'Menus', 'url': reverse('lunch')}]
    return render(request, 'kleep/TODO.html', context)


def store(request):
    context = __base_context__(request)
    context['title'] = 'Loja'
    context['items'] = StoreItem.objects.all()[0:50]
    context['sub_nav'] = [{'name': 'Artigos', 'url': reverse('store')}]
    return render(request, 'kleep/store/items.html', context)


def store_item(request, item_id):
    context = __base_context__(request)
    item = get_object_or_404(StoreItem, id=item_id)
    context['title'] = item.name
    context['item'] = item
    context['sub_nav'] = [{'name': 'Loja', 'url': reverse('store')},
                          {'name': item.name, 'url': reverse('store_item', args=[item_id])}]
    return render(request, 'kleep/store/item.html', context)


def classified_items(request):
    context = __base_context__(request)
    context['title'] = 'Classificados'
    context['items'] = None  # TODO
    context['sub_nav'] = [{'name': 'Classificados', 'url': reverse('classified_items')}]
    return render(request, 'kleep/TODO.html', context)


def classified_item(request, item_id):
    context = __base_context__(request)
    item = None  # TODO
    context['title'] = item.name
    context['item'] = item
    context['sub_nav'] = [{'name': 'Classificados', 'url': reverse('classified_items')},
                          {'name': item.name, 'url': reverse('classified_item', args=[item_id])}]
    return render(request, 'kleep/TODO.html', context)


def feedback(request):
    context = __base_context__(request)
    context['title'] = 'Opiniões'
    context['items'] = None  # TODO
    context['sub_nav'] = [{'name': 'Opiniões', 'url': reverse('feedback')}]
    return render(request, 'kleep/TODO.html', context)


def feedback_idea(request, idea_id):
    context = __base_context__(request)
    idea = None  # TODO
    context['title'] = idea.title
    context['item'] = idea
    context['sub_nav'] = [{'name': 'Opiniões', 'url': reverse('feedback')},
                          {'name': idea.title, 'url': reverse('feedback_idea', args=[idea_id])}]
    return render(request, 'kleep/TODO.html', context)


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
