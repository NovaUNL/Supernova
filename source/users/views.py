from datetime import datetime, timedelta, date
import logging

from dal import autocomplete
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.conf import settings

from users import models as m
from users import forms as f
from users import registrations, exceptions
from college import models as college
from college import schedules
from supernova.views import build_base_context
from .utils import get_students, get_user_stats


def login_view(request):
    context = build_base_context(request)
    context['title'] = "Autenticação"

    if request.user.is_authenticated:
        if 'next' in request.GET:
            return HttpResponseRedirect(request.GET['next'])
        return HttpResponseRedirect(reverse('users:profile', args=[request.user]))

    if request.method == 'POST':
        form = f.LoginForm(data=request.POST)
        if form.is_valid():
            user: m.User = form.get_user()
            login(request, user)

            # First login (TODO change to some sort of tutorial)
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
        return HttpResponseRedirect(request.user.get_absolute_url())

    if 'professor' in request.GET:
        registration_form = f.TeacherRegistrationForm
        student_optional = True
    else:
        registration_form = f.StudentRegistrationForm
        student_optional = False
    context = build_base_context(request)
    context['title'] = "Criar conta"
    context['enabled'] = settings.REGISTRATIONS_ENABLED
    context['student_optional'] = student_optional
    if request.method == 'POST':
        # This is a registration request, validate it
        form = registration_form(data=request.POST)
        valid = form.is_valid()
        if valid:
            registration = form.save(commit=False)
            invite = form.cleaned_data['invite']
            token = registrations.generate_token(settings.REGISTRATIONS_TOKEN_LENGTH)
            registration.token = token
            try:
                try:
                    registrations.email_confirmation(request, registration)
                except Exception as e:
                    raise exceptions.EmailSendingError(str(e))
                registration.save()
                invite.registration = registration
                invite.save()
                return HttpResponseRedirect(reverse('registration_validation'))
            except exceptions.EmailSendingError as e:
                form.add_error(None, "Não foi possível enviar um email. Por favor tenta novamente mais tarde.")
                logging.critical(f"Unable to send email to {registration.email}.\n{e}")
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
            form = registration_form(initial={'invite': invite_token})
            # But warn if the invite token is not valid
            invites = m.Invite.objects.filter(token=invite_token)
            if not invites.exists():
                context['invite_unknown'] = True
        else:
            form = registration_form()
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
    profile_user = cache.get(f'profile_{nickname}')
    if profile_user is None:
        profile_user = get_object_or_404(
            m.User.objects
                .prefetch_related('students', 'teachers', 'groups_custom', 'awards', 'external_pages'),
            nickname=nickname)
        cache.set(f'profile_{nickname}', profile_user, timeout=60 * 10)
    permissions = profile_user.profile_permissions_for(request.user)

    context = build_base_context(request)
    if not permissions["profile_visibility"]:
        context['title'] = context['msg_title'] = 'Insuficiência de permissões'
        context['msg_content'] = 'O perfil deste utilizador está definido como oculto.'
        return render(request, 'supernova/message.html', context)

    context['pcode'] = "u_profile"
    page_name = f"Perfil de {profile_user.name}"
    context['title'] = page_name
    context['profile_user'] = profile_user

    context['permissions'] = permissions
    if permissions['info_visibility'] and profile_user.birth_date:
        now = date.today()
        birth = profile_user.birth_date
        context['age'] = now.year - birth.year - ((now.month, now.day) < (birth.month, birth.day))
    if permissions['enrollments_visibility']:
        primary_students, context['secondary_students'] = get_students(profile_user)
        context['primary_students'] = primary_students
        enrollments = college.Enrollment.objects \
            .select_related('class_instance__parent') \
            .filter(student__in=primary_students)\
            .exclude(disappeared=True) \
            .exclude(class_instance__disappeared=True) \
            .exclude(class_instance__parent__disappeared=True) \
            .all()

        past_enrollments, current_enrollments = [], []
        for e in enrollments:
            if e.class_instance.year == settings.COLLEGE_YEAR and e.class_instance.period == settings.COLLEGE_PERIOD:
                current_enrollments.append(e)
            else:
                past_enrollments.append(e)

        context['current_class_instances'] = a= list(map(lambda e: e.class_instance, current_enrollments))
        context['past_classes'] = b = list(map(lambda e: e.class_instance.parent, past_enrollments))

        if request.user.is_staff:
            context['enrollments_debug'] = college.Enrollment.objects \
                .select_related('class_instance__parent') \
                .filter(student__in=primary_students) \
                .all()

    context['sub_nav'] = [{'name': page_name, 'url': reverse('users:profile', args=[nickname])}]

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
    context['pcode'] = "u_schedule"
    context['title'] = f"Horário de {profile_user.name}"
    context['profile_user'] = profile_user
    context['sub_nav'] = [
        {'name': "Perfil de " + profile_user.name, 'url': reverse('users:profile', args=[nickname])},
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
        {'name': "Perfil de " + user.name, 'url': reverse('users:profile', args=[nickname])},
        {'name': "Calendário", 'url': reverse('users:calendar', args=[nickname])}]
    return render(request, 'users/calendar.html', context)


@login_required
def user_calendar_management_view(request, nickname):
    if request.user.nickname != nickname:
        raise PermissionDenied()
    profile_user = get_object_or_404(m.User.objects, nickname=nickname)

    if 'del' in request.GET:
        try:
            del_id = int(request.GET['del'])
            m.ScheduleEntry.objects.get(id=del_id, user=profile_user).delete()
            return redirect('users:calendar_manage', nickname=nickname)
        except (ValueError, m.ScheduleOnce.DoesNotExist):
            return HttpResponse(status=400)

    once_schedule_entries = m.ScheduleOnce.objects.filter(user=profile_user)
    periodic_schedule_entries = m.SchedulePeriodic.objects.filter(user=profile_user)

    context = build_base_context(request)
    context['profile_user'] = profile_user
    context['pcode'] = "u_calendar_manage"
    context['title'] = "Gerir calendário"
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
        {'name': "Perfil de " + profile_user.name, 'url': reverse('users:profile', args=[nickname])},
        {'name': "Calendário", 'url': reverse('users:calendar', args=[nickname])},
        {'name': "Agenda", 'url': reverse('users:calendar_manage', args=[nickname])}]
    return render(request, 'users/calendar_manage.html', context)


@login_required
def user_reputation_view(request, nickname):
    if request.user.nickname != nickname:
        raise PermissionDenied()
    profile_user = get_object_or_404(m.User.objects, nickname=nickname)

    context = build_base_context(request)
    context['pcode'] = "u_reputation"
    context['title'] = f"Reputação de {profile_user.name}"
    stats = get_user_stats(profile_user)
    context.update(stats)

    context['profile_user'] = profile_user
    context['sub_nav'] = [{'name': profile_user.name, 'url': reverse('users:profile', args=[nickname])},
                          {'name': 'Reputação', 'url': reverse('users:reputation', args=[nickname])}]
    return render(request, 'users/reputation.html', context)


@login_required
def user_evaluations_view(request, nickname):
    if request.user.nickname != nickname:
        raise PermissionDenied()
    profile_user = get_object_or_404(m.User.objects, nickname=nickname)
    context = build_base_context(request)
    context['pcode'] = "u_evaluations"
    context['title'] = f"Avaliações de {profile_user.name}"
    context['profile_user'] = profile_user
    context['enrollments'] = college.Enrollment.objects \
        .filter(student__user=profile_user) \
        .exclude(class_instance__year=settings.COLLEGE_YEAR, class_instance__period__gte=settings.COLLEGE_PERIOD) \
        .select_related('class_instance__parent') \
        .order_by('class_instance__year', 'class_instance__period') \
        .reverse() \
        .all()
    events = college.ClassInstanceEvent.objects \
        .filter(date__gte=datetime.today().date(), class_instance__student__user=profile_user) \
        .select_related('class_instance__parent')
    context['next_evaluations'] = next_evaluations \
        = list(filter(lambda e: e.type in (college.ctypes.EventType.TEST, college.ctypes.EventType.EXAM), events))
    context['next_events'] = list(filter(lambda e: e not in next_evaluations, events))
    context['sub_nav'] = [{'name': profile_user.name, 'url': reverse('users:profile', args=[nickname])},
                          {'name': 'Eventos', 'url': request.get_raw_uri()}]
    return render(request, 'users/profile_evaluations.html', context)


@login_required
def user_profile_settings_view(request, nickname):
    if request.user.nickname != nickname and not request.user.is_staff:
        raise PermissionDenied()
    profile_user = get_object_or_404(m.User, nickname=nickname)
    context = build_base_context(request)

    if request.user.nickname != nickname and request.user.is_staff:
        context['permissions_form'] = f.AccountPermissionsForm(profile_user)
    settings_form = f.AccountSettingsForm(instance=profile_user)

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
                if 'new_password' in settings_form.cleaned_data and settings_form.cleaned_data['new_password']:
                    profile_user.set_password(settings_form.cleaned_data['new_password'])
                    profile_user.save()
                    # Prevent logout locally
                    if profile_user == request.user:
                        login(request, profile_user)

                cache.delete(f'profile_{nickname}')
                return HttpResponseRedirect(reverse('users:profile', args=[profile_user.nickname]))

    context['settings_form'] = settings_form
    context['pcode'] = 'u_settings'
    context['title'] = 'Definições da conta'
    context['profile_user'] = profile_user
    context['sub_nav'] = [
        {'name': "Perfil de " + profile_user.name, 'url': reverse('users:profile', args=[nickname])},
        {'name': "Definições da conta", 'url': reverse('users:settings', args=[nickname])}]

    return render(request, 'users/profile_settings.html', context)


@login_required
@permission_required('users.add_invite', raise_exception=True)
def invites_view(request, nickname):
    if request.user.nickname != nickname and not request.user.is_staff:
        raise PermissionDenied()
    user = get_object_or_404(m.User.objects.prefetch_related('invites'), nickname=nickname)
    context = build_base_context(request)
    context['pcode'] = "u_invites"
    context['title'] = f"Convites emitidos por {user.name}"
    context['profile_user'] = user
    context['sub_nav'] = [{'name': user.name, 'url': reverse('users:profile', args=[nickname])},
                          {'name': 'Convites', 'url': reverse('users:invites', args=[nickname])}]
    return render(request, 'users/invites.html', context)


@login_required
@permission_required('users.add_invite', raise_exception=True)
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
    context['title'] = f"Convites emitidos por {user.name}"
    context['profile_user'] = user
    context['sub_nav'] = [{'name': user.name, 'url': reverse('users:profile', args=[nickname])},
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
