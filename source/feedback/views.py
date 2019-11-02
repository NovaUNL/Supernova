from django.shortcuts import render
from django.urls import reverse

from supernova.views import build_base_context


def feedback_list(request):
    context = build_base_context(request)
    context['title'] = 'Opiniões'
    context['items'] = None  # TODO
    context['sub_nav'] = [{'name': 'Opiniões', 'url': reverse('feedback')}]
    return render(request, 'supernova/TODO.html', context)


def idea(request, idea_id):
    context = build_base_context(request)
    idea = None  # TODO
    context['title'] = idea.title
    context['item'] = idea
    context['sub_nav'] = [{'name': 'Opiniões', 'url': reverse('feedback')},
                          {'name': idea.title, 'url': reverse('feedback_idea', args=[idea_id])}]
    return render(request, 'supernova/TODO.html', context)
