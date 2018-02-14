import psutil
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from kleep.forms import LoginForm
from kleep.models import Service, Building


def index(request):
    form = LoginForm()
    return render(request, 'kleep/index.html', {
        'title': "KLEEarly not a riPoff",  # TODO, change me to something less cringy
        'cpu': cpu_load(),
        'people': 0,  # TODO,
        'form': form
    })


def about(request):
    return render(request, 'kleep/about.html', {
        'title': "Sobre",
        'cpu': cpu_load(),
        'people': 0  # TODO
    })


def beg(request):
    return render(request, 'kleep/beg.html', {
        'title': "Ajudas",
        'cpu': cpu_load(),
        'people': 0  # TODO
    })


def privacy(request):
    return render(request, 'kleep/privacy.html', {
        'title': "Politica de privacidade",
        'cpu': cpu_load(),
        'people': 0  # TODO
    })


def campus(request):
    buildings = Building.objects.all()
    services = Service.objects.all()
    return render(request, 'kleep/campus.html', {
        'title': "Mapa do Campus",
        'sub_nav': [{'name': 'Campus', 'url': '/campus/'}],
        'buildings': buildings,
        'services': services,
        'cpu': cpu_load(),
        'people': 0  # TODO
    })


def building(request, building_id):
    pass  # WIP


def profile(request):
    pass  # WIP


def login(request):
    pass  # WIP


def logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def create_account(request):
    pass  # WIP


def cpu_load():
    cpu_load_val = cache.get('cpu_load')
    if cpu_load_val is None:
        cpu_load_val = psutil.cpu_percent(interval=0.10)  # cache instead of calculating for every request
        cache.set('cpu_load', cpu_load_val, 10)

    if cpu_load_val <= 50.0:
        return 0  # low
    elif cpu_load_val <= 80.0:
        return 1  # medium
    else:
        return 2  # high
