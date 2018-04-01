from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from college.models import Class
from kleep.forms import CreateSynopsisSectionForm
from kleep.views import build_base_context

from synopses.models import Area, Subarea, Topic, Section, SectionTopic, \
    SectionLog, ClassSection


def areas_view(request):
    context = build_base_context(request)
    context['title'] = 'Resumos - Areas de estudo'
    context['areas'] = Area.objects.all()
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
                          {'name': area.name, 'url': reverse('synopses:subarea', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea_id])}]
    return render(request, 'synopses/subarea.html', context)


def topic_view(request, topic_id):
    context = build_base_context(request)
    topic = get_object_or_404(Topic, id=topic_id)
    subarea = topic.sub_area
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


def section_view(request, topic_id, section_id):
    context = build_base_context(request)
    topic = get_object_or_404(Topic, id=topic_id)
    section = get_object_or_404(Section, id=section_id)
    if section not in topic.sections.all():
        return HttpResponseRedirect(reverse('synopsis_topic', args=[topic_id]))
    subarea = topic.sub_area
    area = subarea.area
    context['title'] = topic.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['section'] = section
    section_topic_relation = SectionTopic.objects.filter(topic=topic, section=section).first()
    prev_section = SectionTopic.objects.filter(
        topic=topic, index__lt=section_topic_relation.index).order_by('index').last()
    next_section = SectionTopic.objects.filter(
        topic=topic, index__gt=section_topic_relation.index).order_by('index').first()
    if prev_section:
        context['previous_section'] = prev_section.section
    if next_section:
        context['next_section'] = next_section.section
    context['author_log'] = section.sectionlog_set.distinct('author')
    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])},
                          {'name': section.name, 'url': reverse('synopses:section', args=[topic_id, section_id])}]
    return render(request, 'synopses/section.html', context)


def section_creation_view(request, topic_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    topic = get_object_or_404(Topic, id=topic_id)
    context = build_base_context(request)
    choices = [(0, 'Início')] + list(map(lambda section: (section.id, section.name),
                                         Section.objects.filter(synopsistopic=topic_id)
                                         .order_by('sectiontopic__index').all()))
    if request.method == 'POST':
        form = CreateSynopsisSectionForm(data=request.POST)
        form.fields['after'].choices = choices
        if form.is_valid():
            if form.cleaned_data['after'] == '0':
                index = 1
            else:
                # TODO validate
                index = SectionTopic.objects.get(topic=topic, section_id=form.cleaned_data['after']).index + 1

            for entry in SectionTopic.objects.filter(topic=topic, index__gte=index).all():
                entry.index += 1
                entry.save()

            section = Section(name=form.cleaned_data['name'], content=form.cleaned_data['content'])
            section.save()
            section_topic_rel = SectionTopic(topic=topic, section=section, index=index)
            section_topic_rel.save()
            section_log = SectionLog(author=request.user, section=section)
            section_log.save()
            return HttpResponseRedirect(reverse('synopses:section', args=[topic_id, section.id]))
    else:
        form = CreateSynopsisSectionForm()
        form.fields['after'].choices = choices

    subarea = topic.sub_area
    area = subarea.area
    context['title'] = 'Criar nova entrada em %s' % topic.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['form'] = form

    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])},
                          {'name': 'Criar entrada', 'url': reverse('synopses:create_section', args=[topic_id])}]
    return render(request, 'synopses/generic_form.html', context)


def section_edition_view(request, topic_id, section_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    topic = get_object_or_404(Topic, id=topic_id)
    section = get_object_or_404(Section, id=section_id)
    if not SectionTopic.objects.filter(section=section, topic=topic).exists():
        return HttpResponseRedirect(reverse('synopsis_topic', args=[topic_id]))
    section_topic_rel = SectionTopic.objects.get(section=section, topic=topic)
    context = build_base_context(request)
    choices = [(0, 'Início')]
    for other_section in Section.objects.filter(synopsistopic=topic).order_by(
            'synopsissectiontopic__index').all():
        if other_section == section:
            continue
        choices += ((other_section.id, other_section.name),)

    if request.method == 'POST':
        form = CreateSynopsisSectionForm(data=request.POST)
        form.fields['after'].choices = choices
        if form.is_valid():
            if form.cleaned_data['after'] == '0':
                index = 1
            else:
                index = SectionTopic.objects.get(topic=topic, section_id=form.cleaned_data['after']).index + 1

            if SectionTopic.objects.filter(topic=topic, index=index).exclude(section=section).exists():
                for entry in SectionTopic.objects.filter(topic=topic, index__gte=index).all():
                    entry.index += 1
                    entry.save()

            section.name = form.cleaned_data['name']
            if section.content != form.cleaned_data['content']:
                log = SectionLog(author=request.user, section=section, previous_content=section.content)
                section.content = form.cleaned_data['content']
                log.save()
            section.save()

            section_topic_rel.index = index
            section_topic_rel.save()
            return HttpResponseRedirect(reverse('synopses:section', args=[topic_id, section.id]))
    else:
        prev_topic_section = SectionTopic.objects.filter(
            topic=topic, index__lt=section_topic_rel.index).order_by('index').last()
        if prev_topic_section:
            prev_section_id = prev_topic_section.section.id
        else:
            prev_section_id = 0
        form = CreateSynopsisSectionForm(
            initial={'name': section.name, 'content': section.content, 'after': prev_section_id})
        form.fields['after'].choices = choices

    subarea = topic.sub_area
    area = subarea.area
    context['title'] = 'Editar %s' % section.name
    context['area'] = area
    context['subarea'] = subarea
    context['topic'] = topic
    context['form'] = form

    context['sub_nav'] = [{'name': 'Resumos', 'url': reverse('synopses:areas')},
                          {'name': area.name, 'url': reverse('synopses:area', args=[area.id])},
                          {'name': subarea.name, 'url': reverse('synopses:subarea', args=[subarea.id])},
                          {'name': topic.name, 'url': reverse('synopses:topic', args=[topic_id])},
                          {'name': section.name, 'url': reverse('synopses:section', args=[topic_id, section_id])},
                          {'name': 'Editar', 'url': reverse('synopses:edit_section', args=[topic_id, section_id])}]
    return render(request, 'synopses/generic_form.html', context)


def class_synopsis(request, class_id):
    class_ = get_object_or_404(Class, id=class_id)
    context = build_base_context(request)
    # TODO redo me
    return render(request, 'synopses/class.html', context)


def class_synopsis_section(request, class_id, section_id):
    class_ = get_object_or_404(Class, id=class_id)
    section = get_object_or_404(Section, id=section_id)

    class_synopsis_section = ClassSection.objects.get(section=section,
                                                      class_synopsis__corresponding_class=class_)
    related_sections = ClassSection.objects \
        .filter(class_synopsis__corresponding_class=class_).order_by('index')
    previous_section = related_sections.filter(index__lt=class_synopsis_section.index).last()
    next_section = related_sections.filter(index__gt=class_synopsis_section.index).first()

    context = build_base_context(request)
    department = class_.department
    context['title'] = '%s (%s)' % (class_synopsis_section.section.name, class_.name)
    context['department'] = department
    context['class_obj'] = class_
    context['section'] = class_synopsis_section.section
    context['previous_section'] = previous_section
    context['next_section'] = next_section
    context['sub_nav'] = [{'name': 'Departamentos', 'url': reverse('departments')},
                          {'name': department.name, 'url': reverse('department', args=[department.id])},
                          {'name': class_.name, 'url': reverse('class', args=[class_id])},
                          {'name': 'Resumo', 'url': 'TODO'}]
    return render(request, 'synopses/class_section.html', context)
