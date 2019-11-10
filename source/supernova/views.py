import random
from django.shortcuts import render

from services.utils import get_next_meal_items
from users.forms import LoginForm
from supernova.models import Changelog, Catchphrase
from settings import VERSION
from news.models import NewsItem


def index(request):
    context = build_base_context(request)
    context['title'] = "Mais do que arame torcido"
    context['news'] = NewsItem.objects.order_by('datetime').reverse()[0:5]
    context['changelog'] = Changelog.objects.order_by('date').reverse()[0:3]
    context['catchphrase'] = random.choice(Catchphrase.objects.all())
    context['meal_items'], context['meal_date'], time = get_next_meal_items()
    context['meal_name'] = 'Almoço' if time == 3 else 'Jantar'
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
