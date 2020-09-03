from dal import autocomplete
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from django.forms import HiddenInput
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from college import models as college
from supernova.views import build_base_context
from synopses import forms as f
from synopses import models as m


def areas_view(request):
    context = build_base_context(request)
    context['pcode'] = 'l_synops'
    context['title'] = 'Sínteses - Areas de estudo'
    context['areas'] = m.Area.objects.prefetch_related('subareas').all()
    context['classes'] = \
        college.Class.objects \
            .select_related('department') \
            .annotate(section_count=Count('synopsis_sections')) \
            .filter(section_count__gt=0) \
            .order_by('section_count') \
            .reverse()
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')}]
    return render(request, 'synopses/areas.html', context)


def area_view(request, area_id):
    area = get_object_or_404(
        m.Area.objects,
        id=area_id)
    subareas = area.subareas.annotate(section_count=Count('sections'))

    context = build_base_context(request)
    context['pcode'] = 'l_synopses_area'
    context['title'] = 'Sínteses - Categorias de %s' % area.title
    context['area'] = area
    context['subareas'] = subareas
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.title, 'url': reverse('synopses:area', args=[area_id])}]
    return render(request, 'synopses/area.html', context)


def subarea_view(request, subarea_id):
    subarea = get_object_or_404(
        m.Subarea.objects.select_related('area'),
        id=subarea_id)
    area = subarea.area
    sections = subarea.sections.annotate(children_count=Count('children'))
    context = build_base_context(request)
    context['pcode'] = 'l_synopses_subarea'
    context['title'] = 'Sínteses - %s (%s)' % (subarea.title, area.title)
    context['sections'] = sections
    context['subarea'] = subarea
    context['area'] = area
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.title, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.title, 'url': reverse('synopses:subarea', args=[subarea_id])}]
    return render(request, 'synopses/subarea.html', context)


@login_required
@permission_required('synopses.add_subarea', raise_exception=True)
def subarea_create_view(request, area_id):
    area = get_object_or_404(m.Area, id=area_id)

    if request.method == 'POST':
        form = f.SubareaForm(data=request.POST)
        if form.is_valid():
            new_subarea = form.save()
            return HttpResponseRedirect(reverse('synopses:subarea', args=[new_subarea.id]))
    else:
        form = f.SubareaForm(initial={'area': area})
        form.fields['area'].widget = HiddenInput()

    context = build_base_context(request)
    context['pcode'] = 'l_synopses_subarea'
    context['title'] = 'Criar nova categoria de "%s"' % area.title
    context['area'] = area
    context['form'] = form
    context['action_page'] = reverse('synopses:subarea_create', args=[area_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.title, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': 'Propor nova categoria', 'url': reverse('synopses:subarea_create', args=[area_id])}]
    return render(request, 'synopses/generic_form.html', context)


@login_required
@permission_required('synopses.change_subarea', raise_exception=True)
def subarea_edit_view(request, subarea_id):
    subarea = get_object_or_404(m.Subarea, id=subarea_id)
    area = subarea.area

    if request.method == 'POST':
        form = f.SubareaForm(data=request.POST, instance=subarea)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('synopses:subarea', args=[subarea_id]))
    else:
        form = f.SubareaForm(instance=subarea)

    context = build_base_context(request)
    context['pcode'] = 'l_synopses_subarea'
    context['title'] = 'Editar categoria "%s"' % subarea.title
    context['form'] = form
    context['action_page'] = reverse('synopses:subarea_edit', args=[subarea_id])
    context['action_name'] = 'Aplicar alterações'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.title, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.title, 'url': reverse('synopses:subarea', args=[subarea_id])},
                          {'name': 'Editar', 'url': reverse('synopses:subarea_edit', args=[subarea_id])}]
    return render(request, 'synopses/generic_form.html', context)


# Section display views
def __section_common(section, context):
    """
    Code that is common to every section view.
    :param section: The section that is being shown
    :param context: The template context variable
    """
    context['pcode'] = 'l_synopses_section'
    context['section'] = section
    children = m.Section.objects \
        .filter(parents_intermediary__parent=section) \
        .order_by('parents_intermediary__index').all()
    parents = m.Section.objects \
        .filter(children_intermediary__section=section) \
        .order_by('children_intermediary__index').all()
    context['children'] = children
    context['parents'] = parents
    context['author_log'] = section.log_entries.distinct('author')


def section_view(request, section_id):
    """
    View where a section is displayed as an isolated object.
    """
    section = get_object_or_404(
        m.Section.objects
            .select_related('subarea')
            .prefetch_related('classes'),
        id=section_id)
    context = build_base_context(request)
    __section_common(section, context)
    context['title'] = section.title
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': section.title, 'url': '#'}]
    return render(request, 'synopses/section.html', context)


def subsection_view(request, parent_id, child_id):
    """
    View where a section is displayed as a part of another section.
    """
    parent = get_object_or_404(m.Section, id=parent_id)
    child = get_object_or_404(m.Section, id=child_id)
    context = build_base_context(request)
    __section_common(child, context)
    context['title'] = '%s - %s' % (child.title, parent.title)
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': parent.title, 'url': reverse('synopses:section', args=[parent_id])},
                          {'name': child.title, 'url': '#'}]
    return render(request, 'synopses/section.html', context)


def subarea_section_view(request, subarea_id, section_id):
    """
    View where a section is displayed as direct child of a subarea.
    """
    section = get_object_or_404(m.Section.objects.select_related('subarea__area'), id=section_id)
    subarea = section.subarea
    if subarea.id != subarea_id:
        raise Http404('Mismatched section')
    area = subarea.area
    context = build_base_context(request)
    __section_common(section, context)
    context['title'] = '%s - %s' % (section.title, area.title)
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.title, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.title, 'url': reverse('synopses:subarea', args=[subarea_id])},
                          {'name': section.title, 'url': '#'}]
    return render(request, 'synopses/section.html', context)


def section_authors_view(request, section_id):
    section = get_object_or_404(m.Section.objects.prefetch_related('log_entries__author'), id=section_id)
    context = build_base_context(request)
    context['pcode'] = 'l_synopses_section'
    context['title'] = f"Autores de {section.title}"
    context['section'] = section
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': section.title, 'url': reverse('synopses:section', args=[section_id])},
                          {'name': 'Autores', 'url': '#'}]
    return render(request, 'synopses/section_authors.html', context)


# Section creation views
@login_required
@permission_required('synopses.add_section', raise_exception=True)
def section_create_view(request, parent_id):
    parent = get_object_or_404(m.Section, id=parent_id)
    # Choices (for the 'after' field) are at the parent start, or after any section other than this one
    choices = [(0, 'Início')] + list(map(lambda section: (section.id, section.title),
                                         m.Section.objects.filter(parents_intermediary__parent=parent)
                                         .order_by('parents_intermediary__index').all()))
    if request.method == 'POST':
        section_form = f.SectionEditForm(data=request.POST)
        section_form.fields['after'].choices = choices
        sources_formset = f.SectionSourcesFormSet(
            request.POST, prefix="sources")
        web_resources_formset = f.SectionWebpageResourcesFormSet(
            request.POST, prefix="wp_resources")
        doc_resources_formset = f.SectionDocumentResourcesFormSet(
            request.POST, prefix="doc_resources")
        if section_form.is_valid() \
                and sources_formset.is_valid() \
                and web_resources_formset.is_valid() \
                and doc_resources_formset.is_valid():
            # Obtain the requested index
            if section_form.cleaned_data['after'] == 0:
                index = 1
            else:
                index = m.SectionSubsection.objects.get(parent=parent,
                                                        section_id=section_form.cleaned_data['after']).index + 1

            # Avoid index collisions. If the wanted index is taken by some other section
            if m.SectionSubsection.objects.filter(parent=parent, index=index).exists():
                # Then increment the index of every section with an index >= the desired one.
                # TODO do this at once with an .update + F-expression (?)
                for entry in m.SectionSubsection.objects.filter(parent=parent, index__gte=index) \
                        .order_by('index').reverse().all():
                    entry.index += 1
                    entry.save()

            # Save the new section
            section = section_form.save()

            # Annex it to the parent section in the correct index
            section_parent_rel = m.SectionSubsection(parent=parent, section=section, index=index)
            section_parent_rel.save()

            # Create an empty log entry for the author to be identifiable
            section_log = m.SectionLog(author=request.user, section=section)
            section_log.save()

            # Process the formsets
            for data in sources_formset.save(), web_resources_formset.save(), doc_resources_formset.save():
                data.section = section
                data.save()

            # Redirect to the newly created section
            return HttpResponseRedirect(reverse('synopses:subsection', args=[parent_id, section.id]))
    else:
        # This is a request for the creation form. Fill the possible choices
        section_form = f.SectionEditForm(initial={'after': choices[-1][0]})
        section_form.fields['after'].choices = choices
        sources_formset = f.SectionSourcesFormSet(prefix="sources")
        web_resources_formset = f.SectionWebpageResourcesFormSet(prefix="wp_resources")
        doc_resources_formset = f.SectionDocumentResourcesFormSet(prefix="doc_resources")

    subarea = parent.subarea
    area = subarea.area
    context = build_base_context(request)
    context['pcode'] = 'l_synopses_section'
    context['title'] = 'Criar nova entrada em %s' % parent.title
    context['form'] = section_form
    context['sources_formset'] = sources_formset
    context['web_resources_formset'] = web_resources_formset
    context['doc_resources_formset'] = doc_resources_formset
    context['action_page'] = reverse('synopses:section_create', args=[parent_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.title, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.title, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': parent.title, 'url': reverse('synopses:section', args=[parent_id])},
                          {'name': 'Criar secção'}]
    return render(request, 'synopses/generic_form.html', context)


@login_required
@permission_required('synopses.add_section', raise_exception=True)
def subsection_create_view(request, section_id):
    parent = get_object_or_404(m.Section, id=section_id)
    if request.method == 'POST':
        form = f.SectionChildForm(data=request.POST)
        valid = form.is_valid()
        if valid:
            section = form.save()
            m.SectionSubsection(section=section, parent=parent).save()
            return HttpResponseRedirect(reverse('synopses:subsection', args=[parent.id, section.id]))
    else:
        form = f.SectionChildForm()

    context = build_base_context(request)
    context['pcode'] = 'l_synopses_section'
    context['title'] = 'Criar secção em "%s"' % parent.title
    context['form'] = form
    context['action_page'] = reverse('synopses:subsection_create', args=[section_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': parent.title, 'url': reverse('synopses:section', args=[section_id])},
                          {'name': 'Criar secção', 'url': '#'}]
    return render(request, 'synopses/generic_form.html', context)


@login_required
@permission_required('synopses.add_section', raise_exception=True)
def subarea_section_create_view(request, subarea_id):
    subarea = get_object_or_404(m.Subarea, id=subarea_id)
    area = subarea.area
    if request.method == 'POST':
        form = f.SubareaSectionForm(data=request.POST)
        valid = form.is_valid()
        if valid:
            section = form.save(commit=False)
            if section.subarea != subarea:
                form.add_error('subarea', 'Subarea mismatch')
                valid = False
            if valid:
                section = form.save(commit=False)
                section.content_reduce()
                section.save()
                return HttpResponseRedirect(reverse('synopses:subarea_section', args=[subarea_id, section.id]))
    else:
        form = f.SubareaSectionForm(initial={'subarea': subarea})

    context = build_base_context(request)
    context['pcode'] = 'l_synopses_section'
    context['title'] = 'Criar secção em "%s"' % subarea.title
    context['form'] = form
    context['action_page'] = reverse('synopses:subarea_section_create', args=[subarea_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.title, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.title, 'url': reverse('synopses:subarea', args=[subarea_id])},
                          {'name': 'Criar secção', 'url': '#'}]
    return render(request, 'synopses/generic_form.html', context)


@login_required
@permission_required('synopses.change_section', raise_exception=True)
def section_edit_view(request, section_id):
    section = get_object_or_404(m.Section, id=section_id)
    if request.method == 'POST':
        section_form = f.SectionEditForm(data=request.POST, instance=section)
        sources_formset = f.SectionSourcesFormSet(
            request.POST, instance=section, prefix="sources")
        web_resources_formset = f.SectionWebpageResourcesFormSet(
            request.POST, instance=section, prefix="wp_resources")
        doc_resources_formset = f.SectionDocumentResourcesFormSet(
            request.POST, instance=section, prefix="doc_resources")
        if section_form.is_valid() \
                and sources_formset.is_valid() \
                and web_resources_formset.is_valid() \
                and doc_resources_formset.is_valid():
            # If the section content changed then log the change to prevent vandalism and allow reversion.
            if section.content_ck is not None \
                    and section.content_md is None \
                    and section_form.cleaned_data['content_md'] is not None:
                m.SectionLog.objects.create(author=request.user, section=section, previous_content=section.content_ck)
            else:
                if section.content_md != section_form.cleaned_data['content_md']:
                    m.SectionLog.objects.create(
                        author=request.user,
                        section=section,
                        previous_content=section.content_md)
                if section.content_ck != section_form.cleaned_data['content_ck']:
                    m.SectionLog.objects.create(
                        author=request.user,
                        section=section,
                        previous_content=section.content_ck)
            section = section_form.save(commit=False)
            section.save()

            # Child-Parent M2M needs to be done this way due to the non-null index
            # PS: SectionSubsection's save is overridden
            for parent in section_form.cleaned_data['parents']:
                if not m.SectionSubsection.objects.filter(section=section, parent=parent).exists():
                    m.SectionSubsection(section=section, parent=parent).save()

            section_form.save_m2m()

            sources_formset.save()
            doc_resources_formset.save()
            web_resources_formset.save()
            section.compact_indexes()
            # Redirect user to the updated section
            return HttpResponseRedirect(reverse('synopses:section', args=[section.id]))
    else:
        section_form = f.SectionEditForm(instance=section)
        sources_formset = f.SectionSourcesFormSet(instance=section, prefix="sources")
        web_resources_formset = f.SectionWebpageResourcesFormSet(instance=section, prefix="wp_resources")
        doc_resources_formset = f.SectionDocumentResourcesFormSet(instance=section, prefix="doc_resources")

    context = build_base_context(request)
    context['pcode'] = 'l_synopses_section'
    context['title'] = 'Editar %s' % section.title
    context['section'] = section
    context['form'] = section_form
    context['sources_formset'] = sources_formset
    context['web_resources_formset'] = web_resources_formset
    context['doc_resources_formset'] = doc_resources_formset
    context['action_page'] = reverse('synopses:section_edit', args=[section_id])
    context['action_name'] = 'Editar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': section.title, 'url': reverse('synopses:section', args=[section_id])},
                          {'name': 'Editar'}]
    return render(request, 'synopses/section_management.html', context)


# Class related views
def class_sections_view(request, class_id):
    class_ = get_object_or_404(college.Class, id=class_id)
    context = build_base_context(request)
    context['pcode'] = 'l_synopses_class_section'
    context['title'] = "Sintese de %s" % class_.name
    context['synopsis_class'] = class_
    context['sections'] = class_.synopsis_sections \
        .order_by('classes_rel__index') \
        .annotate(exercise_count=Count('exercises'))
    context['expand'] = 'expand' in request.GET
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': class_.name, 'url': reverse('synopses:class', args=[class_id])}]
    return render(request, 'synopses/class_sections.html', context)


def class_section_view(request, class_id, section_id):
    class_synopsis_section = get_object_or_404(
        m.ClassSection.objects.select_related('corresponding_class', 'section'),
        section_id=section_id, corresponding_class_id=class_id)
    class_ = class_synopsis_section.corresponding_class
    section = class_synopsis_section.section

    context = build_base_context(request)
    __section_common(section, context)
    context['title'] = '%s (%s)' % (class_synopsis_section.section.title, class_.name)
    context['synopsis_class'] = class_
    context['section'] = class_synopsis_section.section
    # FIXME old code to navigate from one section to the next in the same class
    # Get sections of this class, take the one indexed before and the one after.
    # related_sections = m.ClassSection.objects \
    #     .filter(corresponding_class=class_).order_by('index')
    # previous_section = related_sections.filter(index__lt=class_synopsis_section.index).last()
    # next_section = related_sections.filter(index__gt=class_synopsis_section.index).first()
    # if previous_section:
    #     context['previous_section'] = previous_section.section
    # if next_section:
    #     context['next_section'] = next_section.section
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': class_.name, 'url': reverse('synopses:class', args=[class_id])},
                          {'name': section.title,
                           'url': reverse('synopses:class_section', args=[class_id, section_id])}]
    return render(request, 'synopses/section.html', context)


@staff_member_required
def class_manage_sections_view(request, class_id):
    class_ = get_object_or_404(college.Class, id=class_id)
    context = build_base_context(request)
    context['pcode'] = 'l_synopses_manage_sections'
    context['title'] = "Editar secções na sintese de %s" % class_.name
    context['synopsis_class'] = class_
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': class_.name, 'url': reverse('synopses:class', args=[class_id])},
                          {'name': 'Secções', 'url': reverse('synopses:class_manage', args=[class_id])}]
    return render(request, 'synopses/class_management.html', context)


def section_exercises_view(request, section_id):
    section = get_object_or_404(
        m.Section.objects.prefetch_related('exercises'),
        id=section_id)
    context = build_base_context(request)
    context['pcode'] = 'l_synopses_section_exercises'
    context['title'] = "Exercicios em %s" % section.title
    context['section'] = section
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': section.title, 'url': reverse('synopses:section', args=[section_id])},
                          {'name': 'Exercícios'}]
    return render(request, 'synopses/section_exercises.html', context)


class AreaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Area.objects.all()
        if self.q:
            qs = qs.filter(title__istartswith=self.q)
        return qs


class SubareaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Subarea.objects.all()
        if self.q:
            qs = qs.filter(title__istartswith=self.q)
        return qs


class SectionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Section.objects.all()
        if self.q:
            qs = qs.filter(title__contains=self.q)
        return qs
