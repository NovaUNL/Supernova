from django.contrib.auth.decorators import permission_required, login_required
from django.db import models as djm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from exercises.forms import ExerciseForm
from supernova.views import build_base_context
from exercises import models as m
from college import models as college
from synopses import models as synopses
from users.utils import get_students


def index_view(request):
    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = 'Exercícios'
    primary_students, context['secondary_students'] = get_students(request.user)
    classes = college.Class.objects \
        .annotate(exercise_count=djm.Count('synopsis_sections__exercises')) \
        .filter(instances__enrollments__student__in=primary_students) \
        .order_by('name') \
        .all()
    context['classes'] = classes
    context['sub_nav'] = [{'name': 'Exercicios', 'url': reverse('exercises:index')}]
    return render(request, 'exercises/index.html', context)


def exercise_view(request, exercise_id):
    exercise = get_object_or_404(m.Exercise, id=exercise_id)
    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = f'Exercício #{exercise.id}'
    context['exercise'] = exercise
    context['sub_nav'] = [{'name': 'Exercícios', 'url': reverse('exercises:index')},
                          {'name': f'Exercício #{exercise.id}',
                           'url': reverse('exercises:exercise', args=[exercise_id])}]
    return render(request, 'exercises/exercise.html', context)

@login_required
@permission_required('exercises.add_exercise', raise_exception=True)
def create_exercise_view(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.author = request.user
            exercise.save()
            return redirect('exercises:exercise', exercise_id=exercise.id)
    else:
        if 'section' in request.GET:
            section = get_object_or_404(synopses.Section, id=request.GET['section'])
            form = ExerciseForm(initial={'synopses_sections': [section, ]})
        else:
            form = ExerciseForm()

    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = 'Submeter exercício'
    context['form'] = form
    context['sub_nav'] = [{'name': 'Exercícios', 'url': reverse('exercises:index')},
                          {'name': 'Submeter exercício', 'url': reverse('exercises:create')}]
    return render(request, 'exercises/editor.html', context)


@login_required
@permission_required('exercises.change_exercise', raise_exception=True)
def edit_exercise_view(request, exercise_id):
    exercise = get_object_or_404(m.Exercise, id=exercise_id)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            exercise = form.save()
            return redirect('exercises:exercise', exercise_id=exercise.id)
    else:
        form = ExerciseForm(instance=exercise)

    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = f'Editar exercício #{exercise.id}'
    context['form'] = form
    context['sub_nav'] = [{'name': 'Exercícios', 'url': reverse('exercises:index')},
                          {'name': 'Editar exercício', 'url': reverse('exercises:edit', args=[exercise_id])}]
    return render(request, 'exercises/editor.html', context)
