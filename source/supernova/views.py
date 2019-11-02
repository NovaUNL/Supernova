import random
from django.core.cache import cache
from django.shortcuts import render

from users.forms import LoginForm
from supernova.models import Changelog, Catchphrase
from settings import VERSION
from news.models import NewsItem


def index(request):
    context = build_base_context(request)
    context['title'] = "O sistema que não deixa folhas soltas"
    context['news'] = NewsItem.objects.order_by('datetime').reverse()[0:5]
    context['changelog'] = Changelog.objects.order_by('date').reverse()[0:3]
    context['catchphrase'] = random.choice(Catchphrase.objects.all())
    return render(request, 'supernova/index.html', context)


def about(request):
    context = build_base_context(request)
    context['title'] = "Sobre"
    context['version'] = VERSION
    return render(request, 'supernova/about.html', context)


def beg(request):
    context = build_base_context(request)
    context['title'] = "Ajudas"
    return render(request, 'supernova/beg.html', context)


def privacy(request):
    context = build_base_context(request)
    context['title'] = "Política de privacidade"
    return render(request, 'supernova/privacy.html', context)


def build_base_context(request):
    result = {
        'disable_auth': False,
        'sub_nav': None,
    }
    if not request.user.is_authenticated:
        result['login_form'] = LoginForm()
    return result
