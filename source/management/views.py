from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import reverse

from supernova import models as m
from management import forms as f
from supernova.views import build_base_context
from users import models as users


@staff_member_required
def index_view(request):
    context = build_base_context(request)
    context['title'] = "Painel administrativo"
    context['pcode'] = "manag_index"
    context['sub_nav'] = [{'name': 'Painel administrativo', 'url': reverse('management:index')}]
    return render(request, 'management/index.html', context)


@staff_member_required
def users_view(request):
    context = build_base_context(request)
    context['title'] = "Gestão"
    context['pcode'] = "manag_users"
    context['users'] = users.User.objects.all()
    context['latest_registrations'] = users.Registration.objects \
        .order_by('creation') \
        .select_related('requested_student', 'requested_teacher', 'resulting_user', 'invite') \
        .reverse()
    context['suspended_users'] = users.User.objects.order_by('nickname').filter(is_active=False).all()

    context['registrations_with_claimed_teachers'] = users.Registration.objects \
        .order_by('creation') \
        .select_related('requested_student', 'requested_teacher', 'resulting_user', 'invite') \
        .exclude(requested_teacher=None) \
        .exclude(resulting_user=None) \
        .filter(requested_teacher__user=None) \
        .reverse()

    reputation_offset_form = f.ReputationOffsetForm(prefix='reputation_offset_')
    assign_student_form = f.BindStudentToUserForm(prefix='assign_student_')
    assign_teacher_form = f.BindTeacherToUserForm(prefix='assign_teacher_')
    password_reset_form = f.PasswordResetForm(prefix='password_reset_')
    if request.method == 'POST':
        if 'reputation_offset' in request.GET:
            reputation_offset_form = f.ReputationOffsetForm(request.POST, prefix='reputation_offset_')
            if reputation_offset_form.is_valid():
                offset = reputation_offset_form.save()
                offset.issue_notification()
        elif 'assign_student' in request.GET:
            assign_student_form = f.BindStudentToUserForm(request.POST, prefix='assign_student_')
            if assign_student_form.is_valid():
                assign_student_form.save()
        elif 'assign_teacher' in request.GET:
            assign_teacher_form = f.BindTeacherToUserForm(request.POST, prefix='assign_teacher_')
            if assign_teacher_form.is_valid():
                assign_teacher_form.save()
        elif 'password_reset' in request.GET:
            password_reset_form = f.PasswordResetForm(request.POST, prefix='password_reset_')
            if password_reset_form.is_valid():
                context['new_password'] = password_reset_form.save()
    context['reputation_offset_form'] = reputation_offset_form
    context['assign_student_form'] = assign_student_form
    context['assign_teacher_form'] = assign_teacher_form
    context['password_reset_form'] = password_reset_form
    context['sub_nav'] = [{'name': 'Utilizadores', 'url': reverse('management:users')}]
    return render(request, 'management/users.html', context)


@staff_member_required
def announcements_view(request):
    context = build_base_context(request)
    context['title'] = "Anúnciar"
    context['pcode'] = "manag_announcements"

    if request.method == 'POST':
        changelog_form = f.ChangelogForm(request.POST)
        if changelog_form.is_valid():
            entry = changelog_form.save()
            if changelog_form.cleaned_data['broadcast_notification']:
                for receiver in users.User.objects.all():
                    # This cannot be bulk created as it has multiple inheritance
                    m.ChangelogNotification(receiver=receiver, entry=entry)
    else:
        changelog_form = f.ChangelogForm()
    context['changelog_form'] = changelog_form
    context['sub_nav'] = [{'name': 'Anúnciar', 'url': reverse('management:announcements')}]
    return render(request, 'management/announcements.html', context)


@staff_member_required
def activity_view(request):
    context = build_base_context(request)
    context['title'] = "Gestão"
    context['pcode'] = "manag_activity"
    context['latest_registrations'] = users.Registration.objects \
        .order_by('creation') \
        .select_related('requested_student', 'requested_teacher', 'resulting_user', 'invite') \
        .reverse()
    context['latest_activity'] = users.Activity.objects.order_by('timestamp').select_related('user').reverse()[0:10]
    context['suspended_users'] = users.User.objects.order_by('nickname').filter(is_active=False).all()

    context['sub_nav'] = [{'name': 'Alterações', 'url': reverse('management:activity')}]
    return render(request, 'management/activity.html', context)


@staff_member_required
def settings_view(request):
    context = build_base_context(request)
    context['title'] = "Definições"
    context['pcode'] = "manag_settings"
    context['sub_nav'] = [{'name': 'Alterações', 'url': reverse('management:settings')}]
    return render(request, 'management/settings.html', context)
