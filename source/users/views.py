from datetime import datetime, timedelta, timezone

from dal import autocomplete
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

import settings
from . import models as m, exceptions, forms, registrations
from college import models as college
from college import schedules
from supernova.views import build_base_context
from .utils import get_students


def login_view(request):
    context = build_base_context(request)
    context['title'] = "Autenticação"

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
    # Redirect logged users to their profiles
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:profile', args=[request.user.nickname]))

    context = build_base_context(request)
    context['title'] = "Criar conta"
    context['enabled'] = settings.REGISTRATIONS_ENABLED
    if request.method == 'POST':
        # This is a registration request, validate it
        form = forms.RegistrationForm(data=request.POST)
        valid = form.is_valid()
        if valid:
            registration = form.save(commit=False)
            invite = form.cleaned_data['invite']
            try:
                token = registrations.generate_token(settings.REGISTRATIONS_TOKEN_LENGTH)
                registration.token = token
                registration.save()
                try:
                    registrations.email_confirmation(request, registration)
                    invite.registration = registration
                finally:
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
        # Return the registration form
        if 't' in request.GET:
            # If an invite token is in the querystring, populate the form with it
            invite_token = request.GET['t']
            form = forms.RegistrationForm(initial={'invite': invite_token})
            # But warn if the invite token is not valid
            invites = m.Invite.objects.filter(token=invite_token)
            if invites.exists():
                invite = invites.first()
                if invite.registration is not None:
                    context['invite_used'] = True
                elif invite.expiration is None or invite.expiration < datetime.now(timezone.utc):
                    context['invite_expired'] = True
            else:
                context['invite_unknown'] = True
        else:
            form = forms.RegistrationForm()
        context['creation_form'] = form
    return render(request, 'users/registration.html', context)


def registration_validation_view(request):
    # Redirect logged users to their profiles
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:profile', args=[request.user.nickname]))

    context = build_base_context(request)
    if request.method == 'POST':
        data = request.POST
    elif 'email' in request.GET and 'token' in request.GET:
        data = request.GET
    else:
        data = None

    if data is None:
        form = forms.RegistrationValidationForm()
    else:
        if 'token' in data and 'email' in data:
            registration = m.Registration.objects \
                .order_by('creation') \
                .filter(email=data['email'], token=data['token']) \
                .first()
            form = forms.RegistrationValidationForm(instance=registration, data=data)
            if form.is_valid():
                try:
                    user = registrations.validate_token(form.cleaned_data['email'], form.cleaned_data['token'])
                    invite = registration.invites.first()
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
            form = forms.RegistrationValidationForm(data=data)
            form.is_valid()  # Trigger the cleanup

    context['form'] = form
    context['title'] = "Validar registo"
    return render(request, 'users/registration_validation.html', context)


def profile_view(request, nickname):
    # TODO visibility & change 0 bellow to access level
    if request.user.nickname != nickname and not request.user.is_staff:
        raise PermissionDenied()
    context = cache.get(f'profile_{nickname}_{0}_context')
    if context is not None:
        return render(request, 'users/profile.html', context)

    user = get_object_or_404(
        m.User.objects.prefetch_related('students__course', 'memberships', 'social_networks', 'badges'),
        nickname=nickname)
    context = build_base_context(request)
    context['pcode'] = "u_profile"
    page_name = f"Perfil de {user.get_full_name()}"
    context['title'] = page_name
    context['profile_user'] = user
    primary_students, context['secondary_students'] = get_students(user)
    context['primary_students'] = primary_students
    turn_instances = college.TurnInstance.objects \
        .select_related('turn__class_instance__parent') \
        .prefetch_related('room__building') \
        .filter(turn__student__in=primary_students,
                turn__class_instance__year=settings.COLLEGE_YEAR,
                turn__class_instance__period=settings.COLLEGE_PERIOD)
    context['weekday_spans'], context['schedule'], context['unsortable'] = \
        schedules.build_schedule(turn_instances)

    context['current_class_instances'] = college.ClassInstance.objects \
        .select_related('parent') \
        .filter(student__in=primary_students,
                year=settings.COLLEGE_YEAR,
                period=settings.COLLEGE_PERIOD)
    context['sub_nav'] = [{'name': page_name, 'url': reverse('users:profile', args=[nickname])}]
    cache.set(f'profile_{nickname}_{0}_context', context, timeout=3600)
    return render(request, 'users/profile.html', context)


@login_required
def user_schedule_view(request, nickname):
    if request.user.nickname != nickname and not request.user.is_staff:
        raise PermissionDenied()
    context = build_base_context(request)
    if nickname == request.user.nickname:
        user = request.user
    else:
        user = get_object_or_404(m.User.objects.prefetch_related('students'), nickname=nickname)

    primary_students, _ = get_students(user)
    if len(primary_students) == 0:
        return HttpResponseRedirect(reverse('users:profile', args=[nickname]))

    context['pcode'] = "u_schedule"
    context['title'] = "Horário de " + nickname
    context['sub_nav'] = [
        {'name': "Perfil de " + user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
        {'name': "Horário", 'url': reverse('users:schedule', args=[nickname])}]

    turn_instances = college.TurnInstance.objects \
        .select_related('turn__class_instance__parent') \
        .prefetch_related('room__building') \
        .filter(turn__student__in=primary_students,
                turn__class_instance__year=settings.COLLEGE_YEAR,
                turn__class_instance__period=settings.COLLEGE_PERIOD)
    context['weekday_spans'], context['schedule'], context['unsortable'] = schedules.build_schedule(turn_instances)
    return render(request, 'users/profile_schedule.html', context)


@login_required
def user_calendar_view(request, nickname):
    if request.user.nickname != nickname and not request.user.is_staff:
        raise PermissionDenied()
    context = build_base_context(request)
    user = get_object_or_404(m.User.objects, nickname=nickname)
    context['profile_user'] = user
    context['pcode'] = "u_calendar"
    context['title'] = "Calendário de " + nickname
    return render(request, 'users/calendar.html', context)


@login_required
def user_profile_settings_view(request, nickname):
    if request.user.nickname != nickname and not request.user.is_staff:
        raise PermissionDenied()
    profile_user = get_object_or_404(m.User, nickname=nickname)
    context = build_base_context(request)
    context['settings_form'] = forms.AccountSettingsForm(instance=profile_user)
    context['permissions_form'] = forms.AccountPermissionsForm(profile_user)
    if request.method == 'POST':
        if 'permissions' in request.GET:
            if not request.user.is_staff:
                raise PermissionDenied("Only staff accounts can change user permissions.")
            if request.user == profile_user:
                raise PermissionDenied("Changing own permissions is forbidden.")
            permissions_form = forms.AccountPermissionsForm(profile_user, request.POST)
            context['permissions_form'] = permissions_form
            if permissions_form.is_valid():
                permissions_form.save()
                profile_user.refresh_from_db()  # Reload permissions
        else:
            settings_form = forms.AccountSettingsForm(request.POST, request.FILES, instance=profile_user)
            if settings_form.is_valid():
                profile_user = settings_form.save()
                if 'new_password' in settings_form:
                    profile_user.set_password(settings_form.cleaned_data['new_password'])
                return HttpResponseRedirect(reverse('users:profile', args=[profile_user.nickname]))
            else:
                context['settings_form'] = settings_form
    context['social_networks'] = m.SocialNetworkAccount.SOCIAL_NETWORK_CHOICES
    context['pcode'] = 'u_settings'
    context['title'] = 'Definições da conta'
    context['profile_user'] = profile_user
    context['sub_nav'] = [
        {'name': "Perfil de " + profile_user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
        {'name': "Definições da conta", 'url': reverse('users:settings', args=[nickname])}]

    return render(request, 'users/profile_settings.html', context)


@login_required
def invites_view(request, nickname):
    if request.user.nickname != nickname and not request.user.is_staff:
        raise PermissionDenied()
    user = get_object_or_404(m.User.objects.prefetch_related('invites'), nickname=nickname)
    context = build_base_context(request)
    context['pcode'] = "u_invites"
    context['title'] = f"Convites emitidos por {user.get_full_name()}"
    context['profile_user'] = user
    context['sub_nav'] = [{'name': user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
                          {'name': 'Convites', 'url': reverse('users:invites', args=[nickname])}]
    return render(request, 'users/invites.html', context)


@login_required
def create_invite_view(request, nickname):
    if request.user.nickname != nickname:
        raise PermissionDenied()
    user = get_object_or_404(m.User.objects.prefetch_related('invites'), nickname=nickname)
    if 'confirmed' in request.GET and request.GET['confirmed'] == 'true':
        token = registrations.generate_token(10)
        m.Invite(issuer=user, token=token, expiration=(datetime.now() + timedelta(days=2))).save()
        return HttpResponseRedirect(reverse('users:invites', args=[request.user]))

    context = build_base_context(request)
    context['pcode'] = "u_invites"
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
