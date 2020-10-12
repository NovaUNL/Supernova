from datetime import datetime, timedelta, timezone

from dal import autocomplete
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

import settings
from users import models as m
from users import forms as f
from users import registrations, exceptions
from college import models as college
from college import schedules
from supernova.views import build_base_context
from .utils import get_students, get_user_stats, calculate_points


def login_view(request):
    context = build_base_context(request)
    context['title'] = "Autenticação"

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:profile', args=[request.user]))

    if request.method == 'POST':
        form = f.LoginForm(data=request.POST)
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
        context['login_form'] = f.LoginForm()
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
        form = f.RegistrationForm(data=request.POST)
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
            form = f.RegistrationForm(initial={'invite': invite_token})
            # But warn if the invite token is not valid
            invites = m.Invite.objects.filter(token=invite_token)
            if not invites.exists():
                context['invite_unknown'] = True
        else:
            form = f.RegistrationForm()
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
        form = f.RegistrationValidationForm()
    else:
        if 'token' in data and 'email' in data:
            registration = m.Registration.objects \
                .order_by('creation') \
                .get(email=data['email'], token=data['token'])
            form = f.RegistrationValidationForm(instance=registration, data=data)
            if form.is_valid():
                try:
                    user = registrations.validate_token(form.cleaned_data['email'], form.cleaned_data['token'])
                    login(request, user)
                    m.GenericNotification.objects.create(receiver=user, message="Bem vindo ao Supernova!")
                    return HttpResponseRedirect(reverse('users:profile', args=[user.nickname]))
                except exceptions.AccountExists as e:
                    form.add_error(None, str(e))
                except exceptions.ExpiredRegistration as e:
                    form.add_error(None, str(e))
                except exceptions.InvalidToken as e:
                    form.add_error(None, str(e))
        else:
            form = f.RegistrationValidationForm(data=data)
            form.is_valid()  # Trigger the cleanup

    context['form'] = form
    context['title'] = "Validar registo"
    return render(request, 'users/registration_validation.html', context)


def profile_view(request, nickname):
    profile_user = get_object_or_404(m.User.objects, nickname=nickname)
    permissions = profile_user.profile_permissions_for(request.user)

    context = build_base_context(request)
    if not permissions["profile_visibility"]:
        context['title'] = context['msg_title'] = 'Insuficiência de permissões'
        context['msg_content'] = 'O perfil deste utilizador está definido como oculto.'
        return render(request, 'supernova/message.html', context)

    cached_context = cache.get(f'profile_{nickname}_{permissions["checksum"]}')
    if False and cached_context is not None:
        # Override cached with the base context
        context = {**cached_context, **context}
        return render(request, 'users/profile.html', context)
    context['pcode'] = "u_profile"
    page_name = f"Perfil de {profile_user.get_full_name()}"
    context['title'] = page_name
    context['profile_user'] = profile_user

    context['permissions'] = permissions
    if permissions['enrollments_visibility']:
        primary_students, context['secondary_students'] = get_students(profile_user)
        context['primary_students'] = primary_students
        context['current_class_instances'] = current_class_instances = college.ClassInstance.objects \
            .select_related('parent') \
            .order_by('parent__name') \
            .filter(student__in=primary_students,
                    year=settings.COLLEGE_YEAR,
                    period=settings.COLLEGE_PERIOD)

        context['past_classes'] = college.Class.objects \
            .filter(instances__enrollments__student__in=primary_students) \
            .exclude(instances__in=current_class_instances) \
            .order_by('name') \
            .distinct('name')

        if permissions['schedule_visibility']:
            shift_instances = college.ShiftInstance.objects \
                .select_related('shift__class_instance__parent') \
                .prefetch_related('room__building') \
                .filter(shift__student__in=primary_students,
                        shift__class_instance__year=settings.COLLEGE_YEAR,
                        shift__class_instance__period=settings.COLLEGE_PERIOD) \
                .exclude(disappeared=True)
            context['weekday_spans'], context['schedule'], context['unsortable'] = \
                schedules.build_schedule(shift_instances)
    context['sub_nav'] = [{'name': page_name, 'url': reverse('users:profile', args=[nickname])}]
    cache.set(f'profile_{nickname}_{permissions["checksum"]}_context', context, timeout=600)

    return render(request, 'users/profile.html', context)


@login_required
def user_schedule_view(request, nickname):
    if request.user.nickname != nickname and not request.user.is_staff:
        raise PermissionDenied()
    context = build_base_context(request)
    if nickname == request.user.nickname:
        profile_user = request.user
    else:
        profile_user = get_object_or_404(m.User.objects.prefetch_related('students'), nickname=nickname)

    primary_students, _ = get_students(profile_user)
    if len(primary_students) == 0:
        return HttpResponseRedirect(reverse('users:profile', args=[nickname]))

    context['pcode'] = "u_schedule"
    context['title'] = "Horário de " + profile_user.get_full_name()
    context['profile_user'] = profile_user

    shift_instances = college.ShiftInstance.objects \
        .select_related('shift__class_instance__parent') \
        .prefetch_related('room__building') \
        .filter(shift__student__in=primary_students,
                shift__class_instance__year=settings.COLLEGE_YEAR,
                shift__class_instance__period=settings.COLLEGE_PERIOD) \
        .exclude(disappeared=True)

    context['weekday_spans'], context['schedule'], context['unsortable'] = schedules.build_schedule(shift_instances)
    context['sub_nav'] = [
        {'name': "Perfil de " + profile_user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
        {'name': "Horário", 'url': reverse('users:schedule', args=[nickname])}]
    return render(request, 'users/profile_schedule.html', context)


@login_required
def user_calendar_view(request, nickname):
    if request.user.nickname != nickname:
        raise PermissionDenied()
    context = build_base_context(request)
    user = get_object_or_404(m.User.objects, nickname=nickname)
    context['profile_user'] = user
    context['pcode'] = "u_calendar"
    context['title'] = "Calendário de " + nickname
    context['sub_nav'] = [
        {'name': "Perfil de " + user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
        {'name': "Calendário", 'url': reverse('users:calendar', args=[nickname])}]
    return render(request, 'users/calendar.html', context)


@login_required
def user_calendar_management_view(request, nickname):
    if request.user.nickname != nickname:
        raise PermissionDenied()
    context = build_base_context(request)
    profile_user = get_object_or_404(m.User.objects, nickname=nickname)
    context['profile_user'] = profile_user
    context['pcode'] = "u_calendar_manage"
    context['title'] = "Gerir calendário"

    once_schedule_entries = m.ScheduleOnce.objects.filter(user=profile_user)
    periodic_schedule_entries = m.SchedulePeriodic.objects.filter(user=profile_user)
    context['once_entries'] = once_schedule_entries
    context['periodic_entries'] = periodic_schedule_entries

    # Show empty forms by default
    once_form = f.ScheduleOnceForm()
    periodic_form = f.SchedulePeriodicForm()
    if 'type' in request.GET:
        rtype = request.GET['type']
        if rtype == "periodic" and request.method == 'POST':
            filled_form = f.SchedulePeriodicForm(request.POST)
            if filled_form.is_valid():
                entry = filled_form.save(commit=False)
                entry.user = profile_user
                entry.save()
            else:
                periodic_form = filled_form  # Replace empty form with filled form with form filled with errors
        elif rtype == "once" and request.method == 'POST':
            filled_form = f.ScheduleOnceForm(request.POST)
            if filled_form.is_valid():
                entry = filled_form.save(commit=False)
                entry.user = profile_user
                entry.save()
            else:
                once_form = filled_form  # Replace empty form with form filled with errors

    context['once_form'] = once_form
    context['periodic_form'] = periodic_form

    context['sub_nav'] = [
        {'name': "Perfil de " + profile_user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
        {'name': "Calendário", 'url': reverse('users:calendar', args=[nickname])},
        {'name': "Gerir", 'url': reverse('users:calendar_manage', args=[nickname])}]
    return render(request, 'users/calendar_manage.html', context)


@login_required
def user_reputation_view(request, nickname):
    if request.user.nickname != nickname:
        raise PermissionDenied()
    profile_user = get_object_or_404(m.User.objects, nickname=nickname)

    context = build_base_context(request)
    context['pcode'] = "u_reputation"
    context['title'] = f"Reputação de {profile_user.get_full_name()}"
    stats = get_user_stats(profile_user)
    context.update(stats)
    context['profile_user'] = profile_user
    context['sub_nav'] = [{'name': profile_user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
                          {'name': 'Reputação', 'url': reverse('users:reputation', args=[nickname])}]
    return render(request, 'users/reputation.html', context)


@login_required
def user_evaluations_view(request, nickname):
    if request.user.nickname != nickname:
        raise PermissionDenied()
    profile_user = get_object_or_404(m.User.objects, nickname=nickname)
    context = build_base_context(request)
    context['pcode'] = "u_evaluations"
    context['title'] = f"Avaliações de {profile_user.get_full_name()}"
    context['profile_user'] = profile_user
    context['enrollments'] = college.Enrollment.objects\
        .filter(student__user=profile_user) \
        .exclude(class_instance__year=settings.COLLEGE_YEAR, class_instance__period__gte=settings.COLLEGE_PERIOD) \
        .select_related('class_instance__parent') \
        .order_by('class_instance__year', 'class_instance__period')\
        .reverse()\
        .all()
    events = college.ClassInstanceEvent.objects \
        .filter(date__gte=datetime.today().date(), class_instance__student__user=profile_user) \
        .select_related('class_instance__parent')
    context['next_evaluations'] = next_evaluations \
        = list(filter(lambda e: e.type in (college.ctypes.EventType.TEST, college.ctypes.EventType.EXAM), events))
    context['next_events'] = list(filter(lambda e: e not in next_evaluations, events))
    context['sub_nav'] = [{'name': profile_user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
                          {'name': 'Eventos', 'url': request.get_raw_uri()}]
    return render(request, 'users/profile_evaluations.html', context)


@login_required
def user_profile_settings_view(request, nickname):
    if request.user.nickname != nickname and not request.user.is_staff:
        raise PermissionDenied()
    profile_user = get_object_or_404(m.User, nickname=nickname)
    context = build_base_context(request)
    context['settings_form'] = f.AccountSettingsForm(instance=profile_user)

    if request.user.nickname != nickname and request.user.is_staff:
        context['permissions_form'] = f.AccountPermissionsForm(profile_user)

    if request.method == 'POST':
        if 'permissions' in request.GET:
            if not request.user.is_staff:
                raise PermissionDenied("Only staff accounts can change user permissions.")
            if request.user == profile_user:
                raise PermissionDenied("Changing own permissions is forbidden.")
            permissions_form = f.AccountPermissionsForm(profile_user, request.POST)
            context['permissions_form'] = permissions_form
            if permissions_form.is_valid():
                permissions_form.save()
                profile_user.refresh_from_db()  # Reload permissions
        else:
            settings_form = f.AccountSettingsForm(request.POST, request.FILES, instance=profile_user)
            if settings_form.is_valid():
                profile_user = settings_form.save()
                if 'new_password' in settings_form:
                    profile_user.set_password(settings_form.cleaned_data['new_password'])
                    # Prevent logout locally
                    if profile_user == request.user:
                        login(request, profile_user)
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
@permission_required('users.add_invite')
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
@permission_required('users.add_invite')
def create_invite_view(request, nickname):
    if request.user.nickname != nickname:
        raise PermissionDenied()
    user = get_object_or_404(m.User.objects.prefetch_related('invites'), nickname=nickname)
    if 'confirmed' in request.GET and request.GET['confirmed'] == 'true':
        token = registrations.generate_token(10)
        m.Invite.objects.create(issuer=user, token=token, expiration=(datetime.now() + timedelta(days=2)))
        return HttpResponseRedirect(reverse('users:invites', args=[nickname]))

    context = build_base_context(request)
    context['pcode'] = "u_invites"
    context['title'] = f"Convites emitidos por {user.get_full_name()}"
    context['profile_user'] = user
    context['sub_nav'] = [{'name': user.get_full_name(), 'url': reverse('users:profile', args=[nickname])},
                          {'name': 'Convites', 'url': reverse('users:invites', args=[nickname])}]
    return render(request, 'users/invite_new.html', context)


@login_required
def notifications_view(request):
    context = build_base_context(request)
    context['pcode'] = "u_notifications"
    context['title'] = "Notificações"
    context['notifications'] = m.Notification.objects \
        .filter(receiver=request.user) \
        .order_by('issue_timestamp') \
        .reverse() \
        .all()
    context['sub_nav'] = [{'name': 'Notificações', 'url': reverse('users:notifications')}]
    return render(request, 'users/notifications.html', context)


class NicknameAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.User.objects.all()
        if self.q:
            if len(self.q) < 5:
                return []
            return qs.filter(nickname__contains=self.q)
        else:
            return []
