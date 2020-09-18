from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from chat.models import GroupExternalConversation
from documents.models import Document
from groups import permissions
from supernova.views import build_base_context
from groups import models as m
from groups import forms as f


def index_view(request):
    context = build_base_context(request)
    context['title'] = "Grupos"
    context['pcode'] = "g"
    context['groups'] = m.Group.objects.prefetch_related('members').all()
    context['sub_nav'] = [{'name': 'Grupos', 'url': reverse('groups:index')}]
    return render(request, 'groups/groups.html', context)


def institutional_view(request):
    context = build_base_context(request)
    context['title'] = "Grupos"
    context['pcode'] = "g_inst"
    context['groups'] = m.Group.objects.prefetch_related('members').filter(
        Q(type=m.Group.ACADEMIC_ASSOCIATION) | Q(type=m.Group.INSTITUTIONAL)).all()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        {'name': 'Institucionais', 'url': reverse('groups:institutional')}]
    return render(request, 'groups/groups.html', context)


def nuclei_view(request):
    context = build_base_context(request)
    context['title'] = "Grupos"
    context['pcode'] = "g_nucl"
    context['groups'] = m.Group.objects.prefetch_related('members').filter(type=m.Group.NUCLEI).all()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        {'name': 'Núcleos', 'url': reverse('groups:nuclei')}]
    return render(request, 'groups/groups.html', context)


def pedagogic_view(request):
    context = build_base_context(request)
    context['title'] = "Grupos"
    context['pcode'] = "g_ped"
    context['groups'] = m.Group.objects.prefetch_related('members').filter(type=m.Group.PEDAGOGIC).all()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        {'name': 'Pedagogicos', 'url': reverse('groups:pedagogic')}]
    return render(request, 'groups/groups.html', context)


def communities_view(request):
    context = build_base_context(request)
    context['title'] = "Grupos"
    context['pcode'] = "g_com"
    context['groups'] = m.Group.objects.prefetch_related('members').filter(type=m.Group.COMMUNITY).all()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        {'name': 'Comunidades', 'url': reverse('groups:communities')}]
    return render(request, 'groups/groups.html', context)


def group_view(request, group_abbr):
    group = get_object_or_404(m.Group, abbreviation=group_abbr)
    permission_flags = 0 if request.user.is_anonymous else permissions.get_user_group_permissions(request.user, group)
    context = build_base_context(request)
    membership_perms = {
        'is_admin': permission_flags & permissions.IS_ADMIN,
        'can_announce': permission_flags & permissions.CAN_ANNOUNCE,
        'can_modify_roles': permission_flags & permissions.CAN_MODIFY_ROLES,
        'can_change_schedule': permission_flags & permissions.CAN_CHANGE_SCHEDULE}
    context['membership_perms'] = membership_perms
    context['title'] = group.name
    context['group'] = group
    context['pcode'], nav_type = resolve_group_type(group)
    context['activities'] = m.Activity.objects.filter(group=group).order_by('datetime').reverse()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])}]
    return render(request, 'groups/group.html', context)


def announcements_view(request, group_abbr):
    group = get_object_or_404(m.Group, abbreviation=group_abbr)
    context = build_base_context(request)
    context['title'] = f'Anúncios de {group.name}'
    context['group'] = group
    context['pcode'], nav_type = resolve_group_type(group)
    context['announcements'] = m.Announcement.objects.filter(group=group).order_by('datetime').reverse()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])},
        {'name': 'Anúncios', 'url': reverse('groups:announcements', args=[group_abbr])}]
    return render(request, 'groups/announcements.html', context)


def announcement_view(request, group_abbr, announcement_id):
    announcement = get_object_or_404(m.Announcement, id=announcement_id, group__abbreviation=group_abbr)
    group = announcement.group
    context = build_base_context(request)
    context['title'] = announcement.title
    context['group'] = group
    context['announcement'] = announcement
    pcode, nav_type = resolve_group_type(group)
    context['pcode'] = pcode + '_ann'
    context['announcements'] = m.Announcement.objects.filter(group=group).order_by('datetime').reverse()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group.id])},
        {'name': 'Anúncios', 'url': reverse('groups:announcements', args=[group.id])},
        {'name': announcement.title, 'url': reverse('groups:announcement', args=[group.id, announcement.id])}]
    return render(request, 'groups/announcement.html', context)


@login_required
def announce_view(request, group_abbr):
    group = get_object_or_404(m.Group, abbreviation=group_abbr)
    context = build_base_context(request)
    pcode, nav_type = resolve_group_type(group)
    context['pcode'] = pcode + '_announce'
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])},
        {'name': 'Anunciar', 'url': reverse('groups:announce', args=[group_abbr])}]

    permission_flags = permissions.get_user_group_permissions(request.user, group)
    if not (permission_flags & permissions.CAN_ANNOUNCE):
        context['title'] = context['msg_title'] = 'Insuficiência de permissões'
        context['msg_content'] = 'O seu utilizador não tem permissões suficientes para anúnciar pelo grupo.'
        return render(request, 'supernova/message.html', context)

    context['title'] = f'Anúnciar por {group.name}'
    context['group'] = group

    if request.method == 'POST':
        form = f.AnnounceForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.group = group
            announcement.author = request.user
            announcement.save()
            return redirect('groups:announcement', group_abbr=group_abbr, announcement_id=announcement.id)
    else:
        form = f.AnnounceForm()

    context['form'] = form
    return render(request, 'groups/announce.html', context)


def documents_view(request, group_abbr):
    group = get_object_or_404(m.Group, abbreviation=group_abbr)
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


def members_view(request, group_abbr):
    group = get_object_or_404(
        m.Group.objects.prefetch_related('memberships__member', 'memberships__role'),
        abbreviation=group_abbr)
    context = build_base_context(request)
    context['title'] = f'Membros de {group.name}'
    context['group'] = group
    # context['membership' = g
    pcode, nav_type = resolve_group_type(group)
    context['pcode'] = pcode + '_memb'
    context['documents'] = Document.objects.filter(author_group=group).all()
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])},
        {'name': 'Membros', 'url': reverse('groups:members', args=[group_abbr])}]
    return render(request, 'groups/members.html', context)


@login_required
def contact_view(request, group_abbr):
    group = get_object_or_404(m.Group, abbreviation=group_abbr)
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


@login_required
def settings_view(request, group_abbr):
    group = get_object_or_404(m.Group, abbreviation=group_abbr)
    context = build_base_context(request)
    pcode, nav_type = resolve_group_type(group)
    context['pcode'] = pcode + '_settings'
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])},
        {'name': 'Definições', 'url': reverse('groups:settings', args=[group_abbr])}]

    permission_flags = permissions.get_user_group_permissions(request.user, group)
    if not (permission_flags & permissions.IS_ADMIN):
        context['title'] = context['msg_title'] = 'Insuficiência de permissões'
        context['msg_content'] = 'O seu utilizador não tem permissões suficientes para mudar as definições do grupo.'
        return render(request, 'supernova/message.html', context)

    context['title'] = f'Definições de {group.name}'
    context['group'] = group

    if request.method == 'POST':
        group_form = f.GroupForm(group, request.POST, instance=group)
        if group_form.is_valid():
            group_form.save()
            return redirect('groups:group', group_abbr=group_abbr)
    else:
        group_form = f.GroupForm(group, instance=group)

    context['group_form'] = group_form
    return render(request, 'groups/settings.html', context)


@login_required
def roles_view(request, group_abbr):
    group = get_object_or_404(m.Group, abbreviation=group_abbr)
    context = build_base_context(request)
    pcode, nav_type = resolve_group_type(group)
    context['pcode'] = pcode + '_roles'
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])},
        {'name': 'Cargos', 'url': reverse('groups:roles', args=[group_abbr])}]

    permission_flags = permissions.get_user_group_permissions(request.user, group)
    if not (permission_flags & permissions.CAN_MODIFY_ROLES or permission_flags & permissions.CAN_ASSIGN_ROLES):
        context['title'] = context['msg_title'] = 'Insuficiência de permissões'
        context['msg_content'] = 'O seu utilizador não tem permissões suficientes para mudar os cargos do grupo.'
        return render(request, 'supernova/message.html', context)

    context['title'] = f'Gerir cargos de {group.name}'
    context['group'] = group
    context['can_edit'] = permission_flags & permissions.CAN_MODIFY_ROLES
    if request.method == 'POST':
        membership_formset = f.GroupMembershipFormSet(
            request.POST,
            instance=group,
            queryset=group.memberships)
        if membership_formset.is_valid():
            # TODO forbid assignment of roles more permissive than the issuer has
            membership = membership_formset.save(commit=False)
            # Delete any tagged object
            for association in membership_formset.deleted_objects:
                association.delete()
            # Add new objects
            for association in membership:
                association.save()
    else:
        membership_formset = f.GroupMembershipFormSet(
            instance=group,
            queryset=group.memberships)

    context['membership_formset'] = membership_formset
    return render(request, 'groups/roles.html', context)


@login_required
def role_view(request, group_abbr, role_id):
    group = get_object_or_404(m.Group, abbreviation=group_abbr)
    context = build_base_context(request)
    pcode, nav_type = resolve_group_type(group)
    context['pcode'] = pcode + '_role'
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])},
        {'name': 'Cargos', 'url': reverse('groups:roles', args=[group_abbr])}]

    permission_flags = permissions.get_user_group_permissions(request.user, group)
    if not permission_flags & permissions.CAN_MODIFY_ROLES:
        context['title'] = context['msg_title'] = 'Insuficiência de permissões'
        context['msg_content'] = 'O seu utilizador não tem permissões suficientes para mudar os cargos do grupo.'
        return render(request, 'supernova/message.html', context)

    context['group'] = group
    context['role_id'] = role_id

    if role_id == 0:
        context['title'] = f'Criar cargo'
        if request.method == 'POST':
            form = f.RoleForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('groups:roles', group_abbr=group_abbr)
        else:
            form = f.RoleForm()
            context['sub_nav'].append({'name': "Criar cargo", 'url': reverse('groups:role', args=[group_abbr, 0])})
    else:
        role = get_object_or_404(m.Role, id=role_id, group__abbreviation=group_abbr)
        if request.method == 'POST':
            form = f.RoleForm(request.POST, instance=role)
            if form.is_valid():
                form.save()
                return redirect('groups:roles', group_abbr=group_abbr)
        else:
            form = f.RoleForm(instance=role)

        context['role'] = role
        context['title'] = f'Edição do cargo {role.name}'
        context['sub_nav'].append({'name': role.name, 'url': reverse('groups:role', args=[group_abbr, role_id])})
    context['form'] = form
    return render(request, 'groups/role.html', context)


@login_required
def schedule_view(request, group_abbr):
    group = get_object_or_404(m.Group, abbreviation=group_abbr)
    context = build_base_context(request)
    pcode, nav_type = resolve_group_type(group)
    context['pcode'] = pcode + '_cal_man'
    context['sub_nav'] = [
        {'name': 'Grupos', 'url': reverse('groups:index')},
        nav_type,
        {'name': group.abbreviation, 'url': reverse('groups:group', args=[group_abbr])},
        {'name': 'Agenda', 'url': reverse('groups:schedule', args=[group_abbr])}]

    permission_flags = permissions.get_user_group_permissions(request.user, group)
    if not permission_flags & permissions.CAN_CHANGE_SCHEDULE:
        context['title'] = context['msg_title'] = 'Insuficiência de permissões'
        context['msg_content'] = 'O seu utilizador não tem permissões suficientes para alterar a agenda do grupo.'
        return render(request, 'supernova/message.html', context)

    context['group'] = group
    once_schedule_entries = m.ScheduleOnce.objects.filter(group=group)
    periodic_schedule_entries = m.SchedulePeriodic.objects.filter(group=group)
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
                entry.group = group
                entry.save()
                m.ScheduleCreation.objects.create(group=group, author=request.user, entry=entry)
            else:
                periodic_form = filled_form  # Replace empty form with filled form with form filled with errors
        elif rtype == "once" and request.method == 'POST':
            filled_form = f.ScheduleOnceForm(request.POST)
            if filled_form.is_valid():
                entry = filled_form.save(commit=False)
                entry.group = group
                entry.save()
                m.ScheduleCreation.objects.create(group=group, author=request.user, entry=entry)
            else:
                once_form = filled_form  # Replace empty form with form filled with errors

    context['once_form'] = once_form
    context['periodic_form'] = periodic_form

    return render(request, 'groups/schedule.html', context)


class GroupRolesAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        group = self.forwarded.get('group', None)
        if group is None or group == '':
            return []
        qs = m.Role.objects.filter(group=group).all()
        if self.q:
            qs = qs.filter(name__contains=self.q)
        return qs


def resolve_group_type(group):
    code = m.Group.GROUP_CODES[group.type]
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
