from dal import autocomplete
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import HiddenInput
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from college.models import Class
from supernova.views import build_base_context
# from synopses.forms import SectionForm, TopicForm, SubareaForm, SectionSourcesFormSet, SectionResourcesFormSet
from synopses import forms as f
from synopses.models import Area, Subarea, Topic, Section, SectionTopic, \
    SectionLog, ClassSection, SectionSubsection
from users.models import User


def can_edit(user: User):
    return user.is_superuser

def areas_view(request):
    context = build_base_context(request)
    context['title'] = 'Sínteses - Areas de estudo'
    context['areas'] = Area.objects.all()
    context['class_synopses'] = ClassSection.objects.distinct('corresponding_class').all()
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')}]
    return render(request, 'synopses/areas.html', context)


def area_view(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    context = build_base_context(request)
    context['title'] = 'Sínteses - Categorias de %s' % area.name
    context['area'] = area
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area_id])}]
    return render(request, 'synopses/area.html', context)


def subarea_view(request, subarea_id):
    subarea = get_object_or_404(Subarea, id=subarea_id)
    area = subarea.area
    context = build_base_context(request)
    context['title'] = 'Sínteses - %s (%s)' % (subarea.name, area.name)
    context['subarea'] = subarea
    context['area'] = area
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea_id])}]
    return render(request, 'synopses/subarea.html', context)


@user_passes_test(can_edit)
def subarea_create_view(request, area_id):
    area = get_object_or_404(Area, id=area_id)

    if request.method == 'POST':
        form = f.SubareaForm(data=request.POST)
        if form.is_valid():
            new_subarea = form.save()
            return HttpResponseRedirect(reverse('synopses:subarea', args=[new_subarea.id]))
    else:
        form = f.SubareaForm(initial={'area': area})
        form.fields['area'].widget = HiddenInput()

    context = build_base_context(request)
    context['title'] = 'Criar nova categoria de "%s"' % area.name
    context['area'] = area
    context['form'] = form
    context['action_page'] = reverse('synopses:subarea_create', args=[area_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': 'Propor nova categoria', 'url': reverse('synopses:subarea_create', args=[area_id])}]
    return render(request, 'synopses/generic_form.html', context)


@user_passes_test(can_edit)
def subarea_edit_view(request, subarea_id):
    subarea = get_object_or_404(Subarea, id=subarea_id)
    area = subarea.area

    if request.method == 'POST':
        form = f.SubareaForm(data=request.POST, instance=subarea)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('synopses:subarea', args=[subarea_id]))
    else:
        form = f.SubareaForm(instance=subarea)

    context = build_base_context(request)
    context['title'] = 'Editar categoria "%s"' % subarea.name
    context['form'] = form
    context['action_page'] = reverse('synopses:subarea_edit', args=[subarea_id])
    context['action_name'] = 'Aplicar alterações'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea_id])},
                          {'name': 'Editar', 'url': reverse('synopses:subarea_edit', args=[subarea_id])}]
    return render(request, 'synopses/generic_form.html', context)


@user_passes_test(can_edit)
def subarea_section_create_view(request, subarea_id):
    subarea = get_object_or_404(Subarea, id=subarea_id)
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
    context['title'] = 'Criar secção em "%s"' % subarea.name
    context['form'] = form
    context['action_page'] = reverse('synopses:subarea_section_create', args=[subarea_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea_id])},
                          {'name': 'Criar secção', 'url': '#'}]
    return render(request, 'synopses/generic_form.html', context)


def subarea_section_view(request, subarea_id, section_id):
    context = build_base_context(request)
    subarea = get_object_or_404(Subarea, id=subarea_id)
    area = subarea.area
    section = get_object_or_404(Section, id=section_id)
    context['section'] = section
    context['author_log'] = section.sectionlog_set.distinct('author')
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea_id])},
                          {'name': section.name, 'url': '#'}]
    return render(request, 'synopses/section.html', context)


def section_view(request, section_id):
    context = build_base_context(request)
    section = get_object_or_404(Section, id=section_id)
    context['section'] = section
    context['author_log'] = section.sectionlog_set.distinct('author')
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': section.name, 'url': '#'}]
    return render(request, 'synopses/section.html', context)


def subsection_view(request, parent_id, child_id):
    context = build_base_context(request)
    parent = get_object_or_404(Section, id=parent_id)
    child = get_object_or_404(Section, id=child_id)
    context['section'] = child
    context['author_log'] = child.sectionlog_set.distinct('author')
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': parent.name, 'url': reverse('synopses:section', args=[parent_id])},
                          {'name': child.name, 'url': '#'}]
    return render(request, 'synopses/section.html', context)


@user_passes_test(can_edit)
def subsection_create_view(request, section_id):
    parent = get_object_or_404(Section, id=section_id)
    if request.method == 'POST':
        form = f.SectionChildForm(data=request.POST)
        valid = form.is_valid()
        if valid:
            section = form.save()
            SectionSubsection(section=section, parent=parent).save()
            return HttpResponseRedirect(reverse('synopses:subsection', args=[parent.id, section.id]))
    else:
        form = f.SectionChildForm()

    context = build_base_context(request)
    context['title'] = 'Criar secção em "%s"' % parent.name
    context['form'] = form
    context['action_page'] = reverse('synopses:subsection_create', args=[section_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': parent.name, 'url': reverse('synopses:section', args=[section_id])},
                          {'name': 'Criar secção', 'url': '#'}]
    return render(request, 'synopses/generic_form.html', context)


def d_topic_view(request, topic_id):
    context = build_base_context(request)
    topic = get_object_or_404(Topic, id=topic_id)
    subarea = topic.subarea
    area = subarea.area
    context['title'] = topic.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['sections'] = topic.sections.order_by('sectiontopic__index').all()
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])}]
    return render(request, 'synopses/topic.html', context)


@user_passes_test(can_edit)
def section_create_view(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    context = build_base_context(request)
    # Choices (for the 'after' field) are at the topic start, or after any section other than this one
    choices = [(0, 'Início')] + list(map(lambda section: (section.id, section.name),
                                         Section.objects.filter(topic=topic)
                                         .order_by('sectiontopic__index').all()))
    if request.method == 'POST':
        section_form = f.SectionEditForm(data=request.POST)
        section_form.fields['after'].choices = choices
        sources_formset = f.SectionSourcesFormSet(request.POST, prefix="sources")
        resources_formset = f.SectionResourcesFormSet(request.POST, prefix="resources")
        if section_form.is_valid() and sources_formset.is_valid() and resources_formset.is_valid():
            # Obtain the requested index
            if section_form.cleaned_data['after'] == 0:
                index = 1
            else:
                index = SectionTopic.objects.get(topic=topic, section_id=section_form.cleaned_data['after']).index + 1

            # Avoid index collisions. If the wanted index is taken by some other section
            if SectionTopic.objects.filter(topic=topic, index=index).exists():
                # Then increment the index of every section with an index >= the desired one.
                for entry in SectionTopic.objects.filter(topic=topic, index__gte=index) \
                        .order_by('index').reverse().all():
                    entry.index += 1
                    entry.save()

            # Save the new section
            section = section_form.save()

            # Annex it to the topic where it was created
            section_topic_rel = SectionTopic(topic=topic, section=section, index=index)
            section_topic_rel.save()

            # Create an empty log entry for the author to be identifiable
            section_log = SectionLog(author=request.user, section=section)
            section_log.save()

            # Process the sources subform
            sources = sources_formset.save()
            for source in sources:
                source.section = section
                source.save()

            # Redirect to the newly created section
            return HttpResponseRedirect(reverse('synopses:topic_section', args=[topic_id, section.id]))
    else:
        # This is a request for the creation form. Fill the possible choices
        section_form = f.SectionEditForm(initial={'after': choices[-1][0]})
        section_form.fields['after'].choices = choices
        sources_formset = f.SectionSourcesFormSet(prefix="sources")
        resources_formset = f.SectionResourcesFormSet(prefix="resources")

    subarea = topic.subarea
    area = subarea.area
    context['title'] = 'Criar nova entrada em %s' % topic.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['form'] = section_form
    context['sources_formset'] = sources_formset
    context['resources_formset'] = resources_formset
    context['action_page'] = reverse('synopses:section_create', args=[topic_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])},
                          {'name': 'Criar entrada'}]
    return render(request, 'synopses/generic_form.html', context)


@user_passes_test(can_edit)
def section_edit_view(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    context = build_base_context(request)

    if request.method == 'POST':
        section_form = f.SectionEditForm(data=request.POST, instance=section)
        sources_formset = f.SectionSourcesFormSet(
            request.POST, instance=section, prefix="sources", queryset=section.sources.all())
        resources_formset = f.SectionResourcesFormSet(request.POST, instance=section, prefix="resources")
        if section_form.is_valid() and sources_formset.is_valid() and resources_formset.is_valid():
            # If the section content changed then log the change to prevent vandalism and allow reversion.
            if section.content != section_form.cleaned_data['content']:
                log = SectionLog(author=request.user, section=section, previous_content=section.content)
                log.save()
            section = section_form.save(commit=False)
            section.save()

            # Child-Parent M2M needs to be done this way due to the non-null index
            # PS: SectionSubsection's save is overridden
            for parent in section_form.cleaned_data['parents']:
                if not SectionSubsection.objects.filter(section=section, parent=parent).exists():
                    SectionSubsection(section=section, parent=parent).save()

            section_form.save_m2m()

            # Process the sources subform
            sources = sources_formset.save()
            # Delete any tagged object
            for source in sources_formset.deleted_objects:
                source.delete()
            # Add new objects
            for source in sources:
                source.section = section
                source.save()

            # Process the resources subform
            resources = resources_formset.save()
            # Delete any tagged object
            for resource in resources_formset.deleted_objects:
                resource.delete()
            # Add new objects
            for resource in resources:
                resource.save()

            # Redirect user to the updated section
            return HttpResponseRedirect(reverse('synopses:section', args=[section.id]))
    else:
        section_form = f.SectionEditForm(instance=section)
        sources_formset = f.SectionSourcesFormSet(instance=section, prefix="sources")
        resources_formset = f.SectionResourcesFormSet(instance=section, prefix="resources")

    context['title'] = 'Editar %s' % section.name
    context['form'] = section_form
    context['sources_formset'] = sources_formset
    context['resources_formset'] = resources_formset
    context['action_page'] = reverse('synopses:section_edit', args=[section_id])
    context['action_name'] = 'Editar'

    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': section.name, 'url': reverse('synopses:section', args=[section_id])},
                          {'name': 'Editar'}]
    return render(request, 'synopses/generic_form.html', context)


def class_sections_view(request, class_id):
    context = build_base_context(request)
    class_ = get_object_or_404(Class, id=class_id)
    context['title'] = "Sintese de %s" % class_.name
    context['synopsis_class'] = class_
    context['sections'] = Section.objects.filter(class_sections__corresponding_class=class_).order_by(
        'class_sections__index')
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': class_.name, 'url': reverse('synopses:class', args=[class_id])}]
    return render(request, 'synopses/class_sections.html', context)


@user_passes_test(can_edit)
def class_manage_sections_view(request, class_id):
    class_ = get_object_or_404(Class, id=class_id)
    context = build_base_context(request)
    context['title'] = "Editar secções na sintese de %s" % class_.name
    context['synopsis_class'] = class_
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': class_.name, 'url': reverse('synopses:class', args=[class_id])},
                          {'name': 'Secções', 'url': reverse('synopses:class_manage', args=[class_id])}]
    return render(request, 'synopses/class_management.html', context)


def class_section_view(request, class_id, section_id):
    class_ = get_object_or_404(Class, id=class_id)
    section = get_object_or_404(Section, id=section_id)

    class_synopsis_section = ClassSection.objects.get(section=section, corresponding_class=class_)
    # Get sections of this class, take the one indexed before and the one after.
    related_sections = ClassSection.objects \
        .filter(corresponding_class=class_).order_by('index')
    previous_section = related_sections.filter(index__lt=class_synopsis_section.index).last()
    next_section = related_sections.filter(index__gt=class_synopsis_section.index).first()

    context = build_base_context(request)
    department = class_.department
    context['title'] = '%s (%s)' % (class_synopsis_section.section.name, class_.name)
    context['department'] = department
    context['synopsis_class'] = class_
    context['section'] = class_synopsis_section.section
    if previous_section:
        context['previous_section'] = previous_section.section
    if next_section:
        context['next_section'] = next_section.section
    context['author_log'] = section.sectionlog_set.distinct('author')
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': class_.name, 'url': reverse('synopses:class', args=[class_id])},
                          {'name': section.name, 'url': reverse('synopses:class_section', args=[class_id, section_id])}]
    return render(request, 'synopses/section.html', context)


class AreaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Area.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class SubareaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Subarea.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class TopicAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Topic.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class SectionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Section.objects.all()
        if self.q:
            qs = qs.filter(name__contains=self.q)
        return qs
