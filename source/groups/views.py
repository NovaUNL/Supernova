from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from chat.models import GroupExternalConversation
from documents.models import Document
from groups.models import Group, Announcement
from supernova.views import build_base_context


def index_view(request):
    context = build_base_context(request)
    context['title'] = "Grupos"
    context['pcode'] = "g"
    context['groups'] = Group.objects.prefetch_related('members').all()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups:index')}]
    return render(request, 'groups/groups.html', context)


def institutional_view(request):
    context = build_base_context(request)
    context['title'] = "Grupos"
    context['pcode'] = "g_inst"
    context['groups'] = Group.objects.prefetch_related('members').filter(
        Q(type=Group.ACADEMIC_ASSOCIATION) | Q(type=Group.INSTITUTIONAL)).all()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        {'name': 'Institucionais', 'url': reverse('groups:institutional')}]
    return render(request, 'groups/groups.html', context)


def nuclei_view(request):
    context = build_base_context(request)
    context['title'] = "Grupos"
    context['pcode'] = "g_nucl"
    context['groups'] = Group.objects.prefetch_related('members').filter(type=Group.NUCLEI).all()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        {'name': 'Núcleos', 'url': reverse('groups:nuclei')}]
    return render(request, 'groups/groups.html', context)


def pedagogic_view(request):
    context = build_base_context(request)
    context['title'] = "Grupos"
    context['pcode'] = "g_ped"
    context['groups'] = Group.objects.prefetch_related('members').filter(type=Group.PEDAGOGIC).all()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        {'name': 'Pedagogicos', 'url': reverse('groups:pedagogic')}]
    return render(request, 'groups/groups.html', context)


def communities_view(request):
    context = build_base_context(request)
    context['title'] = "Grupos"
    context['pcode'] = "g_com"
    context['groups'] = Group.objects.prefetch_related('members').filter(type=Group.COMMUNITY).all()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        {'name': 'Comunidades', 'url': reverse('groups:communities')}]
    return render(request, 'groups/groups.html', context)


def group_view(request, group_abbr):
    group = get_object_or_404(Group, abbreviation=group_abbr)
    context = build_base_context(request)
    context['title'] = group.name
    context['group'] = group
    context['pcode'], nav_type = resolve_group_type(group)
    context['announcements'] = Announcement.objects.filter(group=group).order_by('datetime').reverse()[:5]
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])}]
    return render(request, 'groups/group.html', context)


def announcements_view(request, group_abbr):
    group = get_object_or_404(Group, abbreviation=group_abbr)
    context = build_base_context(request)
    context['title'] = f'Anúncios de {group.name}'
    context['group'] = group
    context['pcode'], nav_type = resolve_group_type(group)
    context['announcements'] = Announcement.objects.filter(group=group).order_by('datetime').reverse()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])},
        {'name': 'Anúncios', 'url': reverse('groups:announcements', args=[group_abbr])}]
    return render(request, 'groups/announcements.html', context)


def announcement_view(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    group = announcement.group
    context = build_base_context(request)
    context['title'] = announcement.title
    context['group'] = group
    context['announcement'] = announcement
    pcode, nav_type = resolve_group_type(group)
    context['pcode'] = pcode + '_ann'
    context['announcements'] = Announcement.objects.filter(group=group).order_by('datetime').reverse()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group.id])},
        {'name': 'Anúncios', 'url': reverse('groups:announcements', args=[group.id])},
        {'name': announcement.title, 'url': reverse('groups:announcement', args=[group.id, announcement.id])}]
    return render(request, 'groups/announcement.html', context)


def documents_view(request, group_abbr):
    group = get_object_or_404(Group, id=group_abbr)
    context = build_base_context(request)
    context['title'] = f'Documentos de {group.name}'
    context['group'] = group
    pcode, nav_type = resolve_group_type(group)
    context['pcode'] = pcode + '_doc'
    context['documents'] = Document.objects.filter(author_group=group).all()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])},
        {'name': 'Documentos', 'url': reverse('groups:documents', args=[group_abbr])}]
    return render(request, 'groups/documents.html', context)


@login_required
def contact_view(request, group_abbr):
    group = get_object_or_404(Group, id=group_abbr)
    context = build_base_context(request)
    context['title'] = f'Contactar {group.name}'
    context['group'] = group
    pcode, nav_type = resolve_group_type(group)
    context['pcode'] = pcode + '_cnt'
    context['conversations'] = GroupExternalConversation.objects.filter(
        group=group, creator=request.user).order_by('date').reverse()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])},
        {'name': 'Contactar', 'url': reverse('groups:contact', args=[group_abbr])}]
    return render(request, 'groups/conversations.html', context)


def resolve_group_type(group):
    code = Group.GROUP_CODES[group.type]
    pcode = f'g_{code}'
    if code == 'inst':
        nav = {'name': 'Institucionais', 'url': reverse('groups:institutional')}
    elif code == 'nucl':
        nav = {'name': 'Núcleos', 'url': reverse('groups:nuclei')}
    elif code == 'ped':
        nav = {'name': 'Pedagogicos', 'url': reverse('groups:pedagogic')}
    elif code == 'com':
        nav = {'name': 'Comunidades', 'url': reverse('groups:communities')}
    else:
        nav = {'name': '?', 'url': '#'}
    return pcode, nav
