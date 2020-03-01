from dal import autocomplete
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

import settings
from college.models import ClassInstance
from . import models as m, exceptions, forms, registrations
from college import models as college
from college import schedules
from supernova.views import build_base_context


def login_view(request):
    context = build_base_context(request)
    context['title'] = "Autenticação"
    context['disable_auth'] = True  # Disable auth overlay

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:profile', args=[request.user]))

    if request.method == 'POST':
        form = forms.LoginForm(data=request.POST)
        if form.is_valid():
            user: m.User = form.get_user()
            login(request, user)

            if user.last_login is None:
                return HttpResponseRedirect(reverse('users:profile', args=[user.username]))

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
        return HttpResponseRedirect(reverse('users:profile', args=[request.user.nickname]))
    context = build_base_context(request)
    context['title'] = "Criar conta"
    context['disable_auth'] = True  # Disable auth overlay
    context['enabled'] = settings.REGISTRATIONS_ENABLED
    if request.method == 'POST':
        form = forms.RegistrationForm(data=request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            invite = form.cleaned_data['invite']
            try:
                registrations.pre_register(request, registration)
                invite.registration = registration
                invite.save()
                return HttpResponseRedirect(reverse('registration_validation'))
            except exceptions.InvalidUsername as e:
                form.add_error(None, str(e))
            except exceptions.AccountExists as e:
                form.add_error(None, str(e))
            except exceptions.AssignedStudent as e:
                form.add_error(None, str(e))
        context['creation_form'] = form
    else:
        context['creation_form'] = forms.RegistrationForm()
    return render(request, 'users/registration.html', context)


def registration_validation_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:profile', args=[request.user.nickname]))

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
                invite = registration.invite_set.first()
                if invite:
                    invite.resulting_user = user
                    invite.save()
                login(request, user)
                return HttpResponseRedirect(reverse('users:profile', args=[user.nickname]))
            except exceptions.AccountExists as e:
                form.add_error(None, str(e))
            except exceptions.ExpiredRegistration as e:
                form.add_error(None, str(e))
            except exceptions.InvalidToken as e:
                form.add_error(None, str(e))
    else:
        form = forms.RegistrationValidationForm()

    context['form'] = form
    context['title'] = "Validar registo"
    return render(request, 'users/registration_validation.html', context)


def profile_view(request, nickname):
    # TODO visibility & change 0 bellow to access level
    context = cache.get(f'profile_{nickname}_{0}_context')
    if context is not None:
        return render(request, 'users/profile.html', context)

    user = get_object_or_404(
        m.User.objects
            .select_related('primary_student__course')
            .prefetch_related('students', 'memberships', 'social_networks', 'badges'),
        nickname=nickname)
    context = build_base_context(request)
    page_name = f"Perfil de {user.get_full_name()}"
    context['title'] = page_name
    context['profile_user'] = user
    if user.primary_student:
        student = user.primary_student
        context['primary_student'] = student
        turn_instances = college.TurnInstance.objects \
            .select_related('turn__class_instance__parent') \
            .prefetch_related('room__building') \
            .filter(turn__student=student,
                    turn__class_instance__year=settings.COLLEGE_YEAR,
                    turn__class_instance__period=settings.COLLEGE_PERIOD)
        context['weekday_spans'], context['schedule'], context['unsortable'] = \
            schedules.build_schedule(turn_instances)

        context['current_class_instances'] = ClassInstance.objects \
            .select_related('parent') \
            .filter(student=user.primary_student,
                    year=settings.COLLEGE_YEAR,
                    period=settings.COLLEGE_PERIOD)
    context['sub_nav'] = [{'name': page_name, 'url': reverse('users:profile', args=[nickname])}]
    cache.set(f'profile_{nickname}_{0}_context', context, timeout=3600)
    return render(request, 'users/profile.html', context)


@login_required
def user_schedule_view(request, nickname):
    context = build_base_context(request)
    user = get_object_or_404(m.User.objects.select_related('primary_student'), id=request.user.id)

    if user.primary_student is None:
        return HttpResponseRedirect(reverse('users:profile', args=[nickname]))
    student = user.primary_student

    context['page'] = 'profile_schedule'
    context['title'] = "Horário de " + nickname
    context['sub_nav'] = [
        {'name': "Perfil de " + user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
        {'name': "Horário", 'url': reverse('users:schedule', args=[nickname])}]

    turn_instances = college.TurnInstance.objects \
        .select_related('turn__class_instance__parent') \
        .prefetch_related('room__building') \
        .filter(turn__student=student,
                turn__class_instance__year=settings.COLLEGE_YEAR,
                turn__class_instance__period=settings.COLLEGE_PERIOD)
    context['weekday_spans'], context['schedule'], context['unsortable'] = schedules.build_schedule(turn_instances)
    return render(request, 'users/profile_schedule.html', context)


@login_required
def user_profile_settings_view(request, nickname):
    context = build_base_context(request)
    requester: m.User = request.user
    user = get_object_or_404(m.User, nickname=nickname)
    if requester != user:
        raise Exception("TODO make a proper error message")
    if request.method == 'POST':
        form = forms.AccountSettingsForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            if 'new_password' in form:
                user.set_password(form.cleaned_data['new_password'])
            return HttpResponseRedirect(reverse('users:profile', args=[user.nickname]))
        else:
            context['settings_form'] = form
    else:
        context['settings_form'] = forms.AccountSettingsForm(instance=user)
    context['social_networks'] = m.SocialNetworkAccount.SOCIAL_NETWORK_CHOICES
    context['page'] = 'profile_settings'
    context['title'] = 'Definições da conta'
    context['sub_nav'] = [
        {'name': "Perfil de " + user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
        {'name': "Definições da conta", 'url': reverse('users:settings', args=[nickname])}]
    return render(request, 'users/profile_settings.html', context)


@login_required
def invites_view(request, nickname):
    user = get_object_or_404(m.User.objects.prefetch_related('invites'), nickname=nickname)
    context = build_base_context(request)
    context['title'] = f"Convites emitidos por {user.get_full_name()}"
    context['profile_user'] = user
    context['sub_nav'] = [{'name': user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
                          {'name': 'Convites', 'url': reverse('users:invites', args=[nickname])}]
    return render(request, 'users/invites.html', context)


@login_required
def create_invite_view(request, nickname):
    user = get_object_or_404(m.User.objects.prefetch_related('invites'), nickname=nickname)
    context = build_base_context(request)
    context['title'] = f"Convites emitidos por {user.get_full_name()}"
    context['profile_user'] = user
    context['sub_nav'] = [{'name': user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
                          {'name': 'Convites', 'url': reverse('users:invites', args=[nickname])}]
    return render(request, 'users/invite_new.html', context)


class NicknameAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.User.objects.all()
        if self.q:
            if len(self.q) < 5:
                return []
            return qs.filter(nickname__contains=self.q)
        else:
            return []
