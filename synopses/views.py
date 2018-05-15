from dal import autocomplete
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from college.models import Class
from kleep.views import build_base_context
from synopses.forms import SectionForm, TopicForm, SubareaForm, SectionSourcesFormSet

from synopses.models import Area, Subarea, Topic, Section, SectionTopic, \
    SectionLog, ClassSection


def areas_view(request):
    context = build_base_context(request)
    context['title'] = 'Resumos - Areas de estudo'
    context['areas'] = Area.objects.all()
    context['class_synopses'] = ClassSection.objects.distinct('corresponding_class').all()
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')}]
    return render(request, 'synopses/areas.html', context)


def area_view(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    context = build_base_context(request)
    context['title'] = 'Resumos - Categorias de %s' % area.name
    context['area'] = area
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area_id])}]
    return render(request, 'synopses/area.html', context)


def subarea_view(request, subarea_id):
    subarea = get_object_or_404(Subarea, id=subarea_id)
    area = subarea.area
    context = build_base_context(request)
    context['title'] = 'Resumos - %s (%s)' % (subarea.name, area.name)
    context['subarea'] = subarea
    context['area'] = area
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea_id])}]
    return render(request, 'synopses/subarea.html', context)


def subarea_create_view(request, area_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    area = get_object_or_404(Area, id=area_id)

    if request.method == 'POST':
        form = SubareaForm(data=request.POST)
        if form.is_valid():
            new_subarea = form.save()
            return HttpResponseRedirect(reverse('synopses:subarea_create', args=[new_subarea.id]))
    else:
        form = SubareaForm(initial={'area': area})
        form.fields['area'].disabled = True

    context = build_base_context(request)
    context['title'] = 'Criar nova categoria de "%s"' % area.name
    context['area'] = area
    context['form'] = form
    context['action_page'] = reverse('synopses:subarea_create', args=[area_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': 'Propor nova categoria', 'url': reverse('synopses:subarea_create', args=[area_id])}]
    return render(request, 'synopses/generic_form.html', context)


def subarea_edit_view(request, subarea_id):
    subarea = get_object_or_404(Subarea, id=subarea_id)
    area = subarea.area

    if request.method == 'POST':
        form = TopicForm(data=request.POST, instance=subarea)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('synopses:subarea', args=[subarea_id]))
    else:
        form = SubareaForm(instance=subarea)
        form.fields['area'].disabled = True

    context = build_base_context(request)
    context['title'] = 'Editar categoria "%s"' % subarea.name
    context['form'] = form
    context['action_page'] = reverse('synopses:subarea_edit', args=[subarea_id])
    context['action_name'] = 'Aplicar alterações'
    context['sub_nav'] = [{'name': 'Sinteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea_id])},
                          {'name': 'Editar', 'url': reverse('synopses:subarea_edit', args=[subarea_id])}]
    return render(request, 'synopses/generic_form.html', context)


def topic_view(request, topic_id):
    context = build_base_context(request)
    topic = get_object_or_404(Topic, id=topic_id)
    subarea = topic.subarea
    area = subarea.area
    context['title'] = topic.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['sections'] = topic.sections.order_by('sectiontopic__index').all()
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])}]
    return render(request, 'synopses/topic.html', context)


def topic_create_view(request, subarea_id):
    subarea = get_object_or_404(Subarea, id=subarea_id)

    if request.method == 'POST':
        form = TopicForm(data=request.POST)
        if form.is_valid():
            topic = form.save()
            return HttpResponseRedirect(reverse('synopses:topic', args=[topic.id]))
    else:
        form = TopicForm(initial={'subarea': subarea})
        form.fields['subarea'].disabled = True

    context = build_base_context(request)
    context['title'] = 'Criar tópico em "%s"' % subarea.name
    context['form'] = form
    context['action_page'] = reverse('synopses:topic_create', args=[subarea_id])
    context['action_name'] = 'Criar'
    return render(request, 'synopses/generic_form.html', context)


def topic_edit_view(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    subarea = topic.subarea
    area = subarea.area

    if request.method == 'POST':
        form = TopicForm(data=request.POST, instance=topic)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('synopses:topic', args=[topic_id]))
    else:
        form = TopicForm(instance=topic)

    context = build_base_context(request)
    context['title'] = 'Editar tópico "%s"' % topic.name
    context['form'] = form
    context['action_page'] = reverse('synopses:topic_edit', args=[topic_id])
    context['action_name'] = 'Aplicar alterações'
    context['sub_nav'] = [{'name': 'Sinteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])},
                          {'name': 'Editar', 'url': reverse('synopses:topic_edit', args=[topic_id])}]
    return render(request, 'synopses/generic_form.html', context)


def topic_manage_sections_view(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    subarea = topic.subarea
    area = subarea.area
    context = build_base_context(request)
    context['title'] = 'Editar secções em "%s"' % topic.name
    context['topic'] = topic
    context['subarea'] = subarea
    context['area'] = area
    context['topic'] = topic
    context['action_page'] = reverse('synopses:topic_manage', args=[topic_id])
    context['action_name'] = 'Aplicar alterações'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])},
                          {'name': 'Secções', 'url': reverse('synopses:topic_manage', args=[topic_id])}]
    return render(request, 'synopses/topic_management.html', context)


def section_view(request, section_id):
    context = build_base_context(request)
    section = get_object_or_404(Section, id=section_id)
    context['section'] = section
    context['author_log'] = section.sectionlog_set.distinct('author')
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('synopses:areas')},
                          {'name': section.name, 'url': '#'}]
    return render(request, 'synopses/section.html', context)


def topic_section_view(request, topic_id, section_id):
    context = build_base_context(request)
    topic = get_object_or_404(Topic, id=topic_id)
    section = get_object_or_404(Section, id=section_id)
    if section not in topic.sections.all():  # If this section doesn't belong to the topic, redirect to topic
        return HttpResponseRedirect(reverse('synopses:topic', args=[topic_id]))
    subarea = topic.subarea
    area = subarea.area

    # Get sections of this topic, take the one indexed before and the one after.
    section_topic_relation = SectionTopic.objects.filter(topic=topic, section=section).first()
    prev_section = SectionTopic.objects.filter(
        topic=topic, index__lt=section_topic_relation.index).order_by('index').last()
    next_section = SectionTopic.objects.filter(
        topic=topic, index__gt=section_topic_relation.index).order_by('index').first()
    if prev_section:
        context['previous_section'] = prev_section.section
    if next_section:
        context['next_section'] = next_section.section

    context['title'] = topic.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['section'] = section
    context['author_log'] = section.sectionlog_set.distinct('author')
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])},
                          {'name': section.name, 'url': reverse('synopses:topic_section', args=[topic_id, section_id])}]
    return render(request, 'synopses/section.html', context)


def section_create_view(request, topic_id):
    if not request.user.is_authenticated:  # Unauthenticated users cannot create
        return HttpResponseRedirect(reverse('login'))
    topic = get_object_or_404(Topic, id=topic_id)
    context = build_base_context(request)
    # Choices (for the 'after' field) are at the topic start, or after any section other than this one
    choices = [(0, 'Início')] + list(map(lambda section: (section.id, section.name),
                                         Section.objects.filter(topic=topic)
                                         .order_by('sectiontopic__index').all()))
    if request.method == 'POST':
        section_form = SectionForm(data=request.POST)
        section_form.fields['after'].choices = choices
        sources_formset = SectionSourcesFormSet(request.POST, prefix="sources")
        if section_form.is_valid():
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
            sources = sources_formset.save(commit=False)
            for source in sources:
                source.section = section
                source.save()

            # Redirect to the newly created section
            return HttpResponseRedirect(reverse('synopses:topic_section', args=[topic_id, section.id]))
    else:
        # This is a request for the creation form. Fill the possible choices
        section_form = SectionForm(initial={'after': choices[-1][0]})
        section_form.fields['after'].choices = choices
        sources_formset = SectionSourcesFormSet(prefix="sources")

    subarea = topic.subarea
    area = subarea.area
    context['title'] = 'Criar nova entrada em %s' % topic.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['form'] = section_form
    context['sources_formset'] = sources_formset
    context['action_page'] = reverse('synopses:section_create', args=[topic_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])},
                          {'name': 'Criar entrada'}]
    return render(request, 'synopses/generic_form.html', context)


def section_edit_view(request, topic_id, section_id):
    if not request.user.is_authenticated:  # Unauthenticated users cannot edit
        return HttpResponseRedirect(reverse('login'))
    topic = get_object_or_404(Topic, id=topic_id)
    section = get_object_or_404(Section, id=section_id)
    # If this section does not exist within this topic, redirect to the topic page
    if not SectionTopic.objects.filter(section=section, topic=topic).exists():
        return HttpResponseRedirect(reverse('synopses:topic', args=[topic_id]))
    section_topic_rel = SectionTopic.objects.get(section=section, topic=topic)
    context = build_base_context(request)
    # Choices (for the 'after' field) are at the topic start, or after any section other than this one
    choices = [(0, 'Início')]
    for other_section in Section.objects.filter(topic=topic).order_by('sectiontopic__index').all():
        if other_section == section:
            continue
        choices += ((other_section.id, other_section.name),)

    if request.method == 'POST':
        section_form = SectionForm(data=request.POST, instance=section)
        sources_formset = SectionSourcesFormSet(
            request.POST, instance=section, prefix="sources", queryset=section.sources.all())
        section_form.fields['after'].choices = choices
        if section_form.is_valid() and sources_formset.is_valid():
            if section_form.cleaned_data['after'] == 0:
                index = 1
            else:
                index = SectionTopic.objects.get(topic=topic, section_id=section_form.cleaned_data['after']).index + 1

            # Avoid index collisions. If the wanted index is taken by some other section
            if SectionTopic.objects.filter(topic=topic, index=index).exclude(section=section).exists():
                # Then increment the index of every section with an index >= the desired one.
                for entry in SectionTopic.objects.filter(topic=topic, index__gte=index) \
                        .order_by('index').reverse().all():
                    entry.index += 1
                    entry.save()
            section_topic_rel.index = index
            section_topic_rel.save()

            # If the section content changed then log the change to prevent vandalism and allow reversion.
            if section.content != section_form.cleaned_data['content']:
                log = SectionLog(author=request.user, section=section, previous_content=section.content)
                log.save()
            section = section_form.save()

            # Process the sources subform
            sources = sources_formset.save(commit=False)
            # Delete any tagged object
            for source in sources_formset.deleted_objects:
                source.delete()
            # Add new objects
            for source in sources:
                source.section = section
                source.save()

            # Redirect user to the updated section
            return HttpResponseRedirect(reverse('synopses:topic_section', args=[topic_id, section.id]))
    else:
        # Get the section which is indexed before this one
        prev_topic_section = SectionTopic.objects.filter(
            topic=topic, index__lt=section_topic_rel.index).order_by('index').last()
        # If it exists mark it in the previous section field (0 means no section, at the start).
        prev_section_id = prev_topic_section.section.id if prev_topic_section else 0
        section_form = SectionForm(instance=section, initial={'after': prev_section_id})
        sources_formset = SectionSourcesFormSet(instance=section, prefix="sources")
        section_form.fields['after'].choices = choices

    subarea = topic.subarea
    area = subarea.area
    context['title'] = 'Editar %s' % section.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['form'] = section_form
    context['sources_formset'] = sources_formset
    context['action_page'] = reverse('synopses:section_edit', args=[topic_id, section_id])
    context['action_name'] = 'Editar'

    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])},
                          {'name': section.name, 'url': reverse('synopses:topic_section', args=[topic_id, section_id])},
                          {'name': 'Editar'}]
    return render(request, 'synopses/generic_form.html', context)


def class_sections_view(request, class_id):
    context = build_base_context(request)
    class_ = get_object_or_404(Class, id=class_id)
    context['title'] = "Sintese de %s" % class_.name
    context['synopsis_class'] = class_
    context['sections'] = Section.objects.filter(class_sections__corresponding_class=class_).order_by(
        'class_sections__index')
    context['sub_nav'] = [{'name': 'Sinteses', 'url': reverse('synopses:areas')},
                          {'name': class_.name, 'url': reverse('synopses:class', args=[class_id])}]
    return render(request, 'synopses/class_sections.html', context)


def class_manage_sections_view(request, class_id):
    class_ = get_object_or_404(Class, id=class_id)
    context = build_base_context(request)
    context['title'] = "Editar secções na sintese de %s" % class_.name
    context['synopsis_class'] = class_
    context['sub_nav'] = [{'name': 'Sinteses', 'url': reverse('synopses:areas')},
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
    context['previous_section'] = previous_section
    context['next_section'] = next_section
    context['author_log'] = section.sectionlog_set.distinct('author')
    context['sub_nav'] = [{'name': 'Sinteses', 'url': reverse('synopses:areas')},
                          {'name': class_.name, 'url': reverse('synopses:class', args=[class_id])},
                          {'name': section.name, 'url': reverse('synopses:class_section', args=[class_id, section_id])}]
    return render(request, 'synopses/class_section.html', context)


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
