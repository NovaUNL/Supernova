from dal import autocomplete
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, F, Max
from django.forms import HiddenInput
from django.http import HttpResponseRedirect, Http404

from django.contrib.auth.decorators import permission_required, login_required
from django.db import models as djm, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from supernova.views import build_base_context
from learning import models as m
from learning import forms as f
from college import models as college
from users.utils import get_students


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
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')}]
    return render(request, 'learning/areas.html', context)


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
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': area.title, 'url': reverse('learning:area', args=[area_id])}]
    return render(request, 'learning/area.html', context)


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
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': area.title, 'url': reverse('learning:area', args=[area.id])},
                          {'name': subarea.title, 'url': reverse('learning:subarea', args=[subarea_id])}]
    return render(request, 'learning/subarea.html', context)


@login_required
@permission_required('learning.add_subarea', raise_exception=True)
def subarea_create_view(request, area_id):
    area = get_object_or_404(m.Area, id=area_id)

    if request.method == 'POST':
        form = f.SubareaForm(data=request.POST)
        if form.is_valid():
            new_subarea = form.save()
            return HttpResponseRedirect(reverse('learning:subarea', args=[new_subarea.id]))
    else:
        form = f.SubareaForm(initial={'area': area})
        form.fields['area'].widget = HiddenInput()

    context = build_base_context(request)
    context['pcode'] = 'l_synopses_subarea'
    context['title'] = 'Criar nova categoria de "%s"' % area.title
    context['area'] = area
    context['form'] = form
    context['action_page'] = reverse('learning:subarea_create', args=[area_id])
    context['action_name'] = 'Criar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': area.title, 'url': reverse('learning:area', args=[area.id])},
                          {'name': 'Propor nova categoria', 'url': reverse('learning:subarea_create', args=[area_id])}]
    return render(request, 'learning/generic_form.html', context)


@login_required
@permission_required('learning.change_subarea', raise_exception=True)
def subarea_edit_view(request, subarea_id):
    subarea = get_object_or_404(m.Subarea, id=subarea_id)
    area = subarea.area

    if request.method == 'POST':
        form = f.SubareaForm(data=request.POST, instance=subarea)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learning:subarea', args=[subarea_id]))
    else:
        form = f.SubareaForm(instance=subarea)

    context = build_base_context(request)
    context['pcode'] = 'l_synopses_subarea'
    context['title'] = 'Editar categoria "%s"' % subarea.title
    context['form'] = form
    context['action_page'] = reverse('learning:subarea_edit', args=[subarea_id])
    context['action_name'] = 'Aplicar alterações'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': area.title, 'url': reverse('learning:area', args=[area.id])},
                          {'name': subarea.title, 'url': reverse('learning:subarea', args=[subarea_id])},
                          {'name': 'Editar', 'url': reverse('learning:subarea_edit', args=[subarea_id])}]
    return render(request, 'learning/generic_form.html', context)


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
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': section.title, 'url': '#'}]
    return render(request, 'learning/section.html', context)


def subsection_view(request, parent_id, child_id):
    """
    View where a section is displayed as a part of another section.
    """
    parent = get_object_or_404(m.Section, id=parent_id)
    child = get_object_or_404(m.Section, id=child_id)
    context = build_base_context(request)
    __section_common(child, context)
    context['title'] = '%s - %s' % (child.title, parent.title)
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': parent.title, 'url': reverse('learning:section', args=[parent_id])},
                          {'name': child.title, 'url': '#'}]
    return render(request, 'learning/section.html', context)


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
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': area.title, 'url': reverse('learning:area', args=[area.id])},
                          {'name': subarea.title, 'url': reverse('learning:subarea', args=[subarea_id])},
                          {'name': section.title, 'url': '#'}]
    return render(request, 'learning/section.html', context)


def section_authors_view(request, section_id):
    section = get_object_or_404(m.Section.objects.prefetch_related('log_entries__author'), id=section_id)
    context = build_base_context(request)
    context['pcode'] = 'l_synopses_section'
    context['title'] = f"Autores de {section.title}"
    context['section'] = section
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': section.title, 'url': reverse('learning:section', args=[section_id])},
                          {'name': 'Autores', 'url': '#'}]
    return render(request, 'learning/section_authors.html', context)


@login_required
@permission_required('learning.add_section', raise_exception=True)
def section_create_view(request, subarea_id=None, parent_id=None):
    subarea, parent = None, None  # Suppress warnings
    if subarea_id is not None:
        subarea = get_object_or_404(m.Subarea, id=subarea_id)
    if parent_id is not None:
        parent = get_object_or_404(m.Section, id=parent_id)

    sources_formset = f.SectionSourcesFormSet(prefix="sources")
    web_resources_formset = f.SectionWebpageResourcesFormSet(prefix="wp_resources")
    doc_resources_formset = f.SectionDocumentResourcesFormSet(prefix="doc_resources")
    if request.method == 'POST':
        section_form = f.SectionCreateForm(data=request.POST)
        if section_form.is_valid():
            if subarea:
                # Save the new section atomically (all or nothing)
                with transaction.atomic():
                    section = section_form.save()
                    section.subarea = subarea
                    section.save()
                    # Create an empty log entry for the author to be identifiable
                    section_log = m.SectionLog(author=request.user, section=section)
                    section_log.save()
            else:
                # Obtain the requested index
                index = m.SectionSubsection.objects \
                    .filter(parent=parent) \
                    .aggregate(Max('index'))['index__max']
                index = 0 if index is None else index + 1

                # Save the new section atomically (all or nothing)
                with transaction.atomic():
                    section = section_form.save()
                    section_parent_rel = m.SectionSubsection(parent=parent, section=section, index=index)
                    section_parent_rel.save()
                    # Create an empty log entry for the author to be identifiable
                    section_log = m.SectionLog(author=request.user, section=section)
                    section_log.save()

            sources_formset = f.SectionSourcesFormSet(
                request.POST,
                prefix="sources",
                instance=section)
            web_resources_formset = f.SectionWebpageResourcesFormSet(
                request.POST,
                prefix="wp_resources",
                instance=section)
            doc_resources_formset = f.SectionDocumentResourcesFormSet(
                request.POST,
                prefix="doc_resources",
                instance=section)
            if sources_formset.is_valid():
                sources_formset.save()
            if web_resources_formset.is_valid():
                # for form in web_resources_formset:  # For some reason this passes the unit tests
                #     form.save()
                web_resources_formset.save()  # While this doesn't... go figure!
            if doc_resources_formset.is_valid():
                # for form in doc_resources_formset:  # For some reason this passes the unit tests
                #     form.save()
                doc_resources_formset.save()

            # Redirect to the newly created section
            if subarea:
                return HttpResponseRedirect(reverse('learning:subarea_section', args=[subarea_id, section.id]))
            else:
                return HttpResponseRedirect(reverse('learning:subsection', args=[parent_id, section.id]))
    else:
        section_form = f.SectionCreateForm()

    context = build_base_context(request)
    context['pcode'] = 'l_synopses_section'
    context['form'] = section_form
    context['sources_formset'] = sources_formset
    context['web_resources_formset'] = web_resources_formset
    context['doc_resources_formset'] = doc_resources_formset
    if subarea:
        area = subarea.area
        context['title'] = 'Criar secção em "%s"' % subarea.title
        context['sub_nav'] = [
            {'name': 'Sínteses', 'url': reverse('learning:areas')},
            {'name': area.title, 'url': reverse('learning:area', args=[area.id])},
            {'name': subarea.title, 'url': reverse('learning:subarea', args=[subarea.id])},
            {'name': 'Criar secção'}]
        context['action_page'] = reverse('learning:subarea_section_create', args=[subarea_id])
    else:
        context['title'] = 'Criar nova entrada em %s' % parent.title
        context['sub_nav'] = [
            {'name': 'Sínteses', 'url': reverse('learning:areas')},
            {'name': '...'},
            {'name': parent.title, 'url': reverse('learning:section', args=[parent_id])},
            {'name': 'Criar secção', 'url': '#'}]
        context['action_page'] = reverse('learning:subsection_create', args=[parent_id])
    return render(request, 'learning/section_management.html', context)


@login_required
@permission_required('learning.change_section', raise_exception=True)
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
            section = section_form.save()
            sources_formset.save()
            doc_resources_formset.save()
            web_resources_formset.save()
            section.compact_indexes()
            # Redirect user to the updated section
            return HttpResponseRedirect(reverse('learning:section', args=[section.id]))
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
    context['action_page'] = reverse('learning:section_edit', args=[section_id])
    context['action_name'] = 'Editar'
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': section.title, 'url': reverse('learning:section', args=[section_id])},
                          {'name': 'Editar'}]
    return render(request, 'learning/section_management.html', context)


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
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': class_.name, 'url': reverse('learning:class', args=[class_id])}]
    return render(request, 'learning/class_sections.html', context)


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
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': class_.name, 'url': reverse('learning:class', args=[class_id])},
                          {'name': section.title,
                           'url': reverse('learning:class_section', args=[class_id, section_id])}]
    return render(request, 'learning/section.html', context)


@staff_member_required
def class_manage_sections_view(request, class_id):
    class_ = get_object_or_404(college.Class, id=class_id)
    context = build_base_context(request)
    context['pcode'] = 'l_synopses_manage_sections'
    context['title'] = "Editar secções na sintese de %s" % class_.name
    context['synopsis_class'] = class_
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': class_.name, 'url': reverse('learning:class', args=[class_id])},
                          {'name': 'Secções', 'url': reverse('learning:class_manage', args=[class_id])}]
    return render(request, 'learning/class_management.html', context)


def section_exercises_view(request, section_id):
    section = get_object_or_404(
        m.Section.objects.prefetch_related('exercises'),
        id=section_id)
    context = build_base_context(request)
    context['pcode'] = 'l_synopses_section_exercises'
    context['title'] = "Exercicios em %s" % section.title
    context['section'] = section
    context['sub_nav'] = [{'name': 'Sínteses', 'url': reverse('learning:areas')},
                          {'name': '...', 'url': '#'},
                          {'name': section.title, 'url': reverse('learning:section', args=[section_id])},
                          {'name': 'Exercícios'}]
    return render(request, 'learning/section_exercises.html', context)


def exercises_view(request):
    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = 'Exercícios'
    context['department_exercises'] = college.Department.objects.filter(extinguished=False) \
        .annotate(exercise_count=djm.Count('classes__synopsis_sections__exercises')) \
        .order_by('exercise_count') \
        .all()
    context['exercise_count'] = m.Exercise.objects.count()
    if not request.user.is_anonymous and request.user.is_student:
        primary_students, context['secondary_students'] = get_students(request.user)
        context['classes'] = college.Class.objects \
            .annotate(exercise_count=djm.Count('synopsis_sections__exercises')) \
            .filter(instances__enrollments__student__in=primary_students) \
            .order_by('name') \
            .all()
    context['sub_nav'] = [{'name': 'Exercicios', 'url': reverse('learning:exercises')}]
    return render(request, 'learning/exercises.html', context)


def exercise_view(request, exercise_id):
    exercise = get_object_or_404(
        m.Exercise.objects
            .select_related('author')
            .annotate(question_count=Count('linked_questions')),
        id=exercise_id)
    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = f'Exercício #{exercise.id}'
    context['exercise'] = exercise
    context['classes'] = college.Class.objects.filter(synopsis_sections__exercises=exercise).distinct()
    context['sub_nav'] = [{'name': 'Exercícios', 'url': reverse('learning:exercises')},
                          {'name': f'#{exercise_id}',
                           'url': reverse('learning:exercise', args=[exercise_id])}]
    return render(request, 'learning/exercise.html', context)


@login_required
@permission_required('learning.add_exercise', raise_exception=True)
def create_exercise_view(request):
    if request.method == 'POST':
        form = f.ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.author = request.user
            exercise.save()
            form.save_m2m()
            return redirect('learning:exercise', exercise_id=exercise.id)
    else:
        if 'section' in request.GET:
            section = get_object_or_404(m.Section, id=request.GET['section'])
            form = f.ExerciseForm(initial={'synopses_sections': [section, ]})
        else:
            form = f.ExerciseForm()

    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = 'Submeter exercício'
    context['form'] = form
    context['sub_nav'] = [{'name': 'Exercícios', 'url': reverse('learning:exercises')},
                          {'name': 'Submeter exercício', 'url': reverse('learning:exercise')}]
    return render(request, 'learning/editor.html', context)


@login_required
@permission_required('learning.change_exercise', raise_exception=True)
def edit_exercise_view(request, exercise_id):
    exercise = get_object_or_404(m.Exercise, id=exercise_id)
    if request.method == 'POST':
        form = f.ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            exercise = form.save()
            return redirect('learning:exercise', exercise_id=exercise.id)
    else:
        form = f.ExerciseForm(instance=exercise)

    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = f'Editar exercício #{exercise.id}'
    context['form'] = form
    context['sub_nav'] = [{'name': 'Exercícios', 'url': reverse('learning:exercises')},
                          {'name': f'#{exercise_id}', 'url': reverse('learning:exercise', args=[exercise_id])},
                          {'name': 'Editar', 'url': reverse('learning:exercise_edit', args=[exercise_id])}]
    return render(request, 'learning/editor.html', context)


def questions_view(request):
    context = build_base_context(request)
    context['pcode'] = 'l_questions'
    context['title'] = 'Dúvidas'
    context['recent_questions'] = m.Question.objects \
        .select_related('user') \
        .annotate(answer_count=Count('answers'))
    context['popular_questions'] = m.Question.objects \
        .order_by(F('upvotes') + F('downvotes')) \
        .select_related('user') \
        .annotate(answer_count=Count('answers'))
    context['sub_nav'] = [{'name': 'Questões', 'url': reverse('learning:questions')}]
    return render(request, 'learning/questions.html', context)


@login_required
@permission_required('learning.add_question', raise_exception=True)
def question_create_view(request):
    context = build_base_context(request)
    context['pcode'] = 'l_question_create'
    context['title'] = 'Colocar dúvida'
    if request.method == 'POST':
        form = f.QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            question.set_vote(request.user, m.PostableVote.UPVOTE)
            return redirect('learning:question', question_id=question.id)
    else:
        context['form'] = f.QuestionForm()
    context['sub_nav'] = [{'name': 'Questões', 'url': reverse('learning:questions')},
                          {'name': 'Colocar questão', 'url': reverse('learning:question_create')}]
    return render(request, 'learning/question_editor.html', context)


def question_view(request, question_id):
    question = get_object_or_404(
        m.Question.objects
            .prefetch_related('answers__comments', 'comments'),
        id=question_id)
    answer_form = None
    status = 200
    if request.user.is_authenticated:
        if request.method == 'POST':
            if not request.user.has_perm('learning.add_questionanswer'):
                context = build_base_context(request)
                context['pcode'] = 'l_question'
                context['title'] = context['msg_title'] = 'Insuficiência de permissões'
                context['msg_content'] = 'O seu utilizador não tem permissões para responder.'
                return render(request, 'supernova/message.html', context, status=403)

            if 'submit' in request.GET and request.GET['submit'] == 'answer':
                answer_form = f.AnswerForm(request.POST)
                if answer_form.is_valid():
                    answer = answer_form.save(commit=False)
                    answer.to = question
                    answer.user = request.user
                    answer.save()
                    # Reload data, new form
                    question.refresh_from_db()
                    answer_form = f.AnswerForm()
            else:
                status = 400
        else:
            answer_form = f.AnswerForm()

    context = build_base_context(request)
    context['pcode'] = 'l_question'
    context['title'] = 'Dúvida: %s' % question.title
    context['question'] = question
    context['answer_form'] = answer_form
    context['sub_nav'] = [{'name': 'Questões', 'url': reverse('learning:questions')},
                          {'name': question.title, 'url': reverse('learning:question', args=[question_id])}]
    return render(request, 'learning/question.html', context, status=status)


class AreaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Area.objects.all()
        if self.q:
            try:
                qs = qs.filter(Q(id=int(self.q)) | Q(title__istartswith=self.q))
            except ValueError:
                qs = qs.filter(title__contains=self.q)
        return qs


class SubareaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Subarea.objects.all()
        if self.q:
            try:
                qs = qs.filter(Q(id=int(self.q)) | Q(title__istartswith=self.q))
            except ValueError:
                qs = qs.filter(title__contains=self.q)
        return qs


class SectionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Section.objects.all()
        if self.q:
            try:
                qs = qs.filter(Q(id=int(self.q)) | Q(title__contains=self.q))
            except ValueError:
                qs = qs.filter(title__contains=self.q)
        return qs


class ExerciseAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Exercise.objects.all()
        if self.q:
            try:
                qs = qs.filter(id=int(self.q))
            except ValueError:
                qs = None
        return qs
