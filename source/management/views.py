from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import reverse

from management.forms import ReputationOffsetForm
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
    if request.method == 'POST':
        if 'reputation_offset' in request.GET:
            reputation_offset_form = ReputationOffsetForm(request.POST)
            if reputation_offset_form.is_valid():
                offset = reputation_offset_form.save()
                offset.issue_notification()
        else:
            reputation_offset_form = ReputationOffsetForm()
    else:
        reputation_offset_form = ReputationOffsetForm()
    context['reputation_offset_form'] = reputation_offset_form
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
