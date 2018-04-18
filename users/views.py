from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from kleep.forms import AccountSettingsForm, ClipLoginForm, LoginForm, AccountCreationForm
from kleep.schedules import build_turns_schedule
from kleep.settings import REGISTRATIONS_ENABLED, COLLEGE_YEAR, COLLEGE_PERIOD
from kleep.views import build_base_context
from users.models import User


def login_view(request):
    context = build_base_context(request)
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
    return render(request, 'users/login.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def account_creation_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('profile', args=[request.user.nickname]))

    context = build_base_context(request)
    context['title'] = "Criação de conta"
    context['enabled'] = REGISTRATIONS_ENABLED
    if request.method == 'POST':
        pass

    else:
        context['creation_form'] = AccountCreationForm()
    return render(request, 'users/create_account.html', context)


def profile_view(request, nickname):
    user = get_object_or_404(User, nickname=nickname)
    context = build_base_context(request)
    page_name = f"Perfil de {user.get_full_name()}"
    context['page'] = 'profile'
    context['title'] = page_name
    if user.students.count() == 1:
        context['student'] = user.students.first()
    else:
        pass  # TODO

    context['sub_nav'] = [{'name': page_name, 'url': reverse('profile', args=[nickname])}]
    return render(request, 'users/profile.html', context)


def user_schedule_view(request, nickname):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    context = build_base_context(request)
    user = get_object_or_404(User, id=request.user.id)

    if user.student_set.exists():
        student = user.student_set.first()  # FIXME
    else:
        return HttpResponseRedirect(reverse('profile', args=[nickname]))
    context['page'] = 'profile_schedule'
    context['title'] = "Horário de " + nickname
    context['sub_nav'] = [{'name': "Perfil de " + user.get_full_name(), 'url': reverse('profile', args=[nickname])},
                          {'name': "Horário", 'url': reverse('profile_schedule', args=[nickname])}]
    turns = student.turns.filter(class_instance__year=COLLEGE_YEAR, class_instance__period_id=COLLEGE_PERIOD).all()
    context['weekday_spans'], context['schedule'], context['unsortable'] = build_turns_schedule(turns)
    return render(request, 'users/profile_schedule.html', context)


def user_profile_settings_view(request, nickname):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    context = build_base_context(request)
    user = User.objects.get(id=request.user.id)
    context['page'] = 'profile_settings'
    context['title'] = "Definições da conta"
    context['sub_nav'] = [{'name': "Perfil de " + user.get_full_name(), 'url': reverse('profile', args=[nickname])},
                          {'name': "Definições", 'url': reverse('profile_settings', args=[nickname])}]
    if request.method == 'POST':
        form = AccountSettingsForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(reverse('index'))
        else:
            context['settings_form'] = form
    else:
        context['settings_form'] = AccountSettingsForm()

    return render(request, 'users/profile_settings.html', context)


def user_clip_crawler_view(request, nickname):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    context = build_base_context(request)
    profile = request.user.profile
    context['page'] = 'profile_crawler'
    context['title'] = "Definições da conta"
    context['sub_nav'] = [{'name': "Perfil de " + profile.name, 'url': reverse('profile', args=[nickname])},
                          {'name': "Agregar CLIP", 'url': reverse('profile_crawler', args=[nickname])}]
    context['profile'] = profile
    if request.method == 'POST':
        pass
    context['clip_login_form'] = ClipLoginForm()

    return render(request, 'users/profile_crawler.html', context)
