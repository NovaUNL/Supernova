from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from kleep import settings
from . import models as m, exceptions, forms, registrations
from college import schedules
from kleep.views import build_base_context


def login_view(request):
    context = build_base_context(request)
    context['title'] = "Autenticação"
    context['disable_auth'] = True  # Disable auth overlay

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('profile', args=[request.user]))

    if request.method == 'POST':
        form = forms.LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if 'next' in request.GET:
                return HttpResponseRedirect(request.GET['next'])
            return HttpResponseRedirect(reverse('index'))
        else:
            context['login_form'] = form
    else:
        context['login_form'] = forms.LoginForm()
    return render(request, 'users/login.html', context)


def logout_view(request):
    logout(request)
    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    return HttpResponseRedirect(reverse('index'))


def registration_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('profile', args=[request.user.nickname]))

    context = build_base_context(request)
    context['title'] = "Criar conta"
    context['disable_auth'] = True  # Disable auth overlay
    context['enabled'] = settings.REGISTRATIONS_ENABLED
    if request.method == 'POST':
        form = forms.RegistrationForm(data=request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registrations.pre_register(request, registration)
            return HttpResponseRedirect(reverse('registration_validation'))
        context['creation_form'] = form
    else:
        context['creation_form'] = forms.RegistrationForm()
    return render(request, 'users/registration.html', context)


def registration_validation_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('profile', args=[request.user.nickname]))

    context = build_base_context(request)
    if request.method == 'POST':
        data = request.POST
    elif 'email' in request.GET and 'token' in request.GET:
        data = request.GET
    else:
        data = None

    if data is not None:
        if 'token' in data and 'email' in data:
            registration = m.Registration.objects \
                .order_by('creation') \
                .filter(email=data['email'], token=data['token']) \
                .first()
            form = forms.RegistrationValidationForm(instance=registration, data=data)
        else:
            form = forms.RegistrationValidationForm(data=data)

        if form.is_valid():
            try:
                user = registrations.validate_token(form.cleaned_data['email'], form.cleaned_data['token'])
                login(request, user)
                return HttpResponseRedirect(reverse('profile', args=[user.id]))
            except exceptions.ExpiredRegistration or exceptions.InvalidToken or exceptions.AccountExists as e:
                form.add_error(None, str(e))
    else:
        form = forms.RegistrationValidationForm()

    context['form'] = form
    context['title'] = "Validar registo"
    return render(request, 'users/registration_validation.html', context)


def profile_view(request, nickname):
    # TODO visibility
    user = get_object_or_404(m.User, nickname=nickname)
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


@login_required
def user_schedule_view(request, nickname):
    context = build_base_context(request)
    user = get_object_or_404(m.User, id=request.user.id)

    if user.students.exists():
        student = user.students.first()  # FIXME
    else:
        return HttpResponseRedirect(reverse('profile', args=[nickname]))
    context['page'] = 'profile_schedule'
    context['title'] = "Horário de " + nickname
    context['sub_nav'] = [{'name': "Perfil de " + user.get_full_name(), 'url': reverse('profile', args=[nickname])},
                          {'name': "Horário", 'url': reverse('profile_schedule', args=[nickname])}]
    turns = student.turns.filter(
        class_instance__year=settings.COLLEGE_YEAR,
        class_instance__period=settings.COLLEGE_PERIOD).all()
    context['weekday_spans'], context['schedule'], context['unsortable'] = schedules.build_turns_schedule(turns)
    return render(request, 'users/profile_schedule.html', context)


@login_required
def user_profile_settings_view(request, nickname):
    context = build_base_context(request)
    user = m.User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = forms.AccountSettingsForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('profile', args=[nickname]))
        else:
            context['settings_form'] = form
    else:
        context['settings_form'] = forms.AccountSettingsForm(instance=user)

    context['page'] = 'profile_settings'
    context['title'] = 'Definições da conta'
    context['sub_nav'] = [{'name': "Perfil de " + user.get_full_name(), 'url': reverse('profile', args=[nickname])},
                          {'name': "Dados pessoais", 'url': reverse('profile_settings', args=[nickname])}]
    return render(request, 'users/profile_settings.html', context)


@login_required
def user_profile_social_view(request, nickname):
    context = build_base_context(request)
    user = m.User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = forms.PasswordChangeForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(reverse('index'))
        else:
            context['password_change_form'] = form
    else:
        context['password_change_form'] = forms.PasswordChangeForm()

    context['page'] = 'profile_social'
    context['title'] = 'Redes sociais'
    context['social_networks'] = m.SocialNetworkAccount.SOCIAL_NETWORK_CHOICES
    context['sub_nav'] = [{'name': "Perfil de " + user.get_full_name(), 'url': reverse('profile', args=[nickname])},
                          {'name': "Redes sociais", 'url': reverse('profile_social', args=[nickname])}]
    return render(request, 'users/profile_social_networks.html', context)


@login_required
def user_profile_password_view(request, nickname):
    context = build_base_context(request)
    user = m.User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = forms.PasswordChangeForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(reverse('index'))
        else:
            context['password_change_form'] = form
    else:
        context['password_change_form'] = forms.PasswordChangeForm()

    context['page'] = 'profile_password'
    context['title'] = 'Alteração de palavra-passe'
    context['sub_nav'] = [{'name': "Perfil de " + user.get_full_name(), 'url': reverse('profile', args=[nickname])},
                          {'name': "Alterar palavra passe", 'url': reverse('profile_password', args=[nickname])}]
    return render(request, 'users/profile_password_change.html', context)


@login_required
def user_clip_crawler_view(request, nickname):
    user = m.User.objects.get(id=request.user.id)
    context = build_base_context(request)
    context['page'] = 'profile_crawler'
    context['title'] = "Definições da conta"
    context['sub_nav'] = [{'name': "Perfil de " + user.get_full_name(), 'url': reverse('profile', args=[nickname])},
                          {'name': "Agregar CLIP", 'url': reverse('profile_crawler', args=[nickname])}]
    if request.method == 'POST':
        pass
    context['clip_login_form'] = forms.ClipLoginForm()

    return render(request, 'users/profile_crawler.html', context)
