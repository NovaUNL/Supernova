from django.shortcuts import render
from django.urls import reverse

from exercises.forms import ExerciseForm, AnswerFormSet
from kleep.views import build_base_context


def create_exercise(request):
    context = build_base_context(request)
    context['title'] = 'Submeter exercício'
    context['sub_nav'] = [{'name': 'Exercicios', 'url': '#TODO'},
                          {'name': 'Submeter exercício', 'url': reverse('exercises:create_exercise')}]
    return render(request, 'exercises/pre_submit.html', context)


def create_qa_exercise(request):
    context = build_base_context(request)
    context['title'] = 'Submeter exercício questão-resposta'
    context['exercise_form'] = ExerciseForm()
    context['sub_nav'] = [{'name': 'Exercicios', 'url': '#TODO'},
                          {'name': 'Submeter exercício', 'url': reverse('exercises:create_exercise')},
                          {'name': 'Questão-resposta', 'url': '#'}]
    return render(request, 'exercises/qa_submit.html', context)


def create_mc_exercise(request):
    context = build_base_context(request)
    context['title'] = 'Submeter exercício de escolha múltipla'
    context['exercise_form'] = ExerciseForm()
    context['answers_formset'] = AnswerFormSet()
    context['sub_nav'] = [{'name': 'Exercicios', 'url': '#TODO'},
                          {'name': 'Submeter exercício', 'url': reverse('exercises:create_exercise')},
                          {'name': 'Escolha múltipla', 'url': '#'}]
    return render(request, 'exercises/multiple_choice_submit.html', context)
