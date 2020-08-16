from django.shortcuts import render
from django.urls import reverse

from exercises.forms import ExerciseForm
from supernova.views import build_base_context


def index(request):
    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = 'Exercicios'
    context['msg_title'] = 'Por fazer'
    context['msg_content'] = 'Esta funcionalidade ainda está inacabada'
    context['sub_nav'] = [{'name': 'Exercicios', 'url': reverse('exercises:index')}]
    return render(request, 'supernova/message.html', context)


def create_exercise(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = ExerciseForm()

    context = build_base_context(request)
    context['pcode'] = 'l_exercises'
    context['title'] = 'Submeter exercício'
    context['form'] = form
    context['sub_nav'] = [{'name': 'Exercicios', 'url': reverse('exercises:index')},
                          {'name': 'Submeter exercício', 'url': reverse('exercises:create')}]
    return render(request, 'exercises/editor.html', context)
