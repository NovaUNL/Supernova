from datetime import datetime
import random

from django.core.cache import cache
from django.db.models import Q, F
from django.shortcuts import render

from scrapper.boinc import boincstats
from services.utils import get_next_meal_items
from supernova.models import Changelog, Catchphrase
from news.models import NewsItem
from college import models as college


def index(request):
    context = build_base_context(request)

    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    minutes = (now - midnight).seconds // 60

    context['title'] = "Perfeição nanométrica"
    context['news'] = NewsItem.objects.order_by('datetime').reverse()[0:6]
    context['changelog'] = Changelog.objects.order_by('date').reverse()[0:3]
    context['meal_items'], context['meal_date'], time = get_next_meal_items()
    context['meal_name'] = 'Almoço' if time == 2 else 'Jantar'
    boinc_users = boincstats.get_team_users(2068385380)
    boinc_users.sort(key=lambda x: -x['weekly'])
    context['boinc_users'] = boinc_users[:3]
    boinc_projects = boincstats.get_team_projects(2068385380)
    boinc_projects.sort(key=lambda x: -x['weekly'])
    context['boinc_projects'] = boinc_projects[:3]

    context['free_rooms'] = college.Room.objects \
        .annotate(turn_instances__end=F('turn_instances__start') + F('turn_instances__duration')) \
        .filter(unlocked=True) \
        .select_related('building') \
        .order_by('building__abbreviation', 'name') \
        .exclude(Q(turn_instances__start__lt=minutes) & Q(turn_instances__end__gt=minutes)) \
        .distinct('building__abbreviation', 'name')

    return render(request, 'supernova/index.html', context)


def build_base_context(request):
    catchphrases = cache.get('catchphrases')
    if catchphrases is None:
        catchphrases = list(Catchphrase.objects.all())
        cache.set('catchphrases', catchphrases, timeout=3600 * 24)
    base_context = {
        'disable_auth': False,
        'sub_nav': None,
        'catchphrase': random.choice(catchphrases)
    }
    return base_context
