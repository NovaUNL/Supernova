from django.shortcuts import render
from django.urls import reverse

from supernova.views import build_base_context


def canteen_view(request):
    context = build_base_context(request)
    context['title'] = "Cantina"
    context['sub_nav'] = [
        {'name': 'Serviços', 'url': reverse('services:canteen')},
        {'name': 'Cantina', 'url': reverse('services:canteen')}]
    return render(request, 'services/cantina.html', context)