from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from chat.models import GroupExternalConversation
from documents.models import Document
from groups.models import Group, Announcement
from kleep.views import build_base_context


def groups_view(request):
    context = build_base_context(request)
    if 'filtro' in request.GET:
        context['type_filter'] = int(request.GET['filtro'])
    context['title'] = "Grupos"
    context['groups'] = Group.objects.all()
    context['group_types'] = Group.GROUP_TYPES
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')}]
    return render(request, 'groups/groups.html', context)


def group_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    context = build_base_context(request)
    context['title'] = group.name
    context['group'] = group
    context['page'] = 'group'
    context['announcements'] = Announcement.objects.filter(group=group).order_by('datetime').reverse()[0:5]
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group_id])}]
    return render(request, 'groups/group.html', context)


def announcements_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    context = build_base_context(request)
    context['title'] = f'Anúncios de {group.name}'
    context['group'] = group
    context['page'] = 'group_anouncements'
    context['announcements'] = Announcement.objects.filter(group=group).order_by('datetime').reverse()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group_id])},
                          {'name': 'Anúncios', 'url': reverse('group_announcement', args=[group_id])}]
    return render(request, 'groups/announcements.html', context)


def announcement_view(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    group = announcement.group
    context = build_base_context(request)
    context['title'] = announcement.title
    context['group'] = group
    context['announcement'] = announcement
    context['page'] = 'group_anouncement'
    context['announcements'] = Announcement.objects.filter(group=group).order_by('datetime').reverse()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group.id])},
                          {'name': 'Anúncios', 'url': reverse('group_announcements', args=[group.id])},
                          {'name': announcement.title, 'url': reverse('group_announcements', args=[group.id])}]
    return render(request, 'groups/announcement.html', context)


def documents_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    context = build_base_context(request)
    context['title'] = f'Documentos de {group.name}'
    context['group'] = group
    context['page'] = 'group_documents'
    context['documents'] = Document.objects.filter(author_group=group).all()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group_id])},
                          {'name': 'Documentos', 'url': reverse('group_documents', args=[group_id])}]
    return render(request, 'groups/documents.html', context)


def contact_view(request, group_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    group = get_object_or_404(Group, id=group_id)
    context = build_base_context(request)
    context['title'] = f'Contactar {group.name}'
    context['group'] = group
    context['page'] = 'group_contact'
    context['conversations'] = GroupExternalConversation.objects.filter(
        group=group, creator=request.user).order_by('date').reverse()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups')},
                          {'name': group.name, 'url': reverse('group', args=[group_id])},
                          {'name': 'Contactar', 'url': reverse('group_contact', args=[group_id])}]
    return render(request, 'groups/conversations.html', context)
