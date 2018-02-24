import psutil
from django.contrib.auth import logout, login
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from kleep.forms import LoginForm
from kleep.models import Service, Building, User


def index(request):
    context = __base_context__(request)
    context['title'] = "KLEEarly not a riPoff"  # TODO, change me to something less cringy
    return render(request, 'kleep/index.html', context)


def about(request):
    context = __base_context__(request)
    context['title'] = "Sobre"
    return render(request, 'kleep/about.html', context)


def beg(request):
    context = __base_context__(request)
    context['title'] = "Ajudas"
    return render(request, 'kleep/beg.html', context)


def privacy(request):
    context = __base_context__(request)
    context['title'] = "Politica de privacidade"
    return render(request, 'kleep/privacy.html', context)


def campus(request):
    context = __base_context__(request)
    context['title'] = "Mapa do campus"
    context['buildings'] = Building.objects.all()
    context['services'] = Service.objects.all()
    context['sub_nav'] = [{'name': 'Campus', 'url': reverse('campus')}, {'name': 'Mapa', 'url': '/campus/'}]
    return render(request, 'kleep/campus.html', context)


def campus_transportation(request):
    context = __base_context__(request)
    context['title'] = "Transportes para o campus"
    context['sub_nav'] = [
        {'name': 'Campus', 'url': reverse('campus')},
        {'name': 'Transportes', 'url': reverse('transportation')}]
    return render(request, 'kleep/transportation.html', context)


def building(request):
    pass  # WIP


def profile(request):
    context = __base_context__(request)
    user = User.objects.get(id=request.user.id)
    page_name = "Perfil de " + user.name
    context['title'] = page_name
    context['sub_nav'] = [{'name': page_name, 'url': reverse('profile')}]
    context['user'] = user
    return render(request, 'kleep/profile.html', context)


def login_view(request):
    context = __base_context__(request)
    context['title'] = "Autenticação"
    context['disable_auth'] = True  # Disable auth overlay

    if request.user.is_authenticated:
        HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(reverse('index'))
        else:
            print("Invalid")
            context['login_form'] = form

    return render(request, 'kleep/login.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def create_account(request):
    pass  # WIP


def __base_context__(request):
    result = {'cpu': __cpu_load__(),
              'people': 0  # TODO
              }
    if not request.user.is_authenticated:
        result['login_form'] = LoginForm()
    return result


def __cpu_load__():
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
