from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from exercises.forms import ExerciseForm
from supernova.views import build_base_context
from exercises import models as m


def index_view(request):
    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = 'Exercicios'
    context['msg_title'] = 'Por fazer'
    context['msg_content'] = 'Esta funcionalidade ainda está inacabada'
    context['sub_nav'] = [{'name': 'Exercicios', 'url': reverse('exercises:index')}]
    return render(request, 'supernova/message.html', context)


def create_exercise_view(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.author = request.user
            exercise.save()
            return redirect('exercises:exercise', exercise_id=exercise.id)
    else:
        form = ExerciseForm()

    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = 'Submeter exercício'
    context['form'] = form
    context['sub_nav'] = [{'name': 'Exercicios', 'url': reverse('exercises:index')},
                          {'name': 'Submeter exercício', 'url': reverse('exercises:create')}]
    return render(request, 'exercises/editor.html', context)


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
    context['title'] = 'Editar exercício'
    context['form'] = form
    context['sub_nav'] = [{'name': 'Exercicios', 'url': reverse('exercises:index')},
                          {'name': 'Editar exercício', 'url': reverse('exercises:edit', args=[exercise_id])}]
    return render(request, 'exercises/editor.html', context)


def exercise_view(request, exercise_id):
    exercise = get_object_or_404(m.Exercise, id=exercise_id)
    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = 'Exercício'
    context['exercise'] = exercise
    context['sub_nav'] = [{'name': 'Exercicios', 'url': reverse('exercises:index')},
                          {'name': 'Exercicio', 'url': reverse('exercises:exercise', args=[exercise_id])}]
    return render(request, 'exercises/exercise.html', context)
