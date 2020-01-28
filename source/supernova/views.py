from datetime import datetime, timedelta
import random
from itertools import chain

from django.core.cache import cache
from django.shortcuts import render

from scrapper.boinc import boincstats
from scrapper.transportation import mts, tst
from services.utils import get_next_meal_items
from users.forms import LoginForm
from supernova.models import Changelog, Catchphrase
from settings import VERSION
from news.models import NewsItem


def index(request):
    context = build_base_context(request)
    context['title'] = "Perfeição nanométrica"
    context['news'] = NewsItem.objects.order_by('datetime').reverse()[0:6]
    context['changelog'] = Changelog.objects.order_by('date').reverse()[0:3]
    context['catchphrase'] = random.choice(Catchphrase.objects.all())
    context['meal_items'], context['meal_date'], time = get_next_meal_items()
    context['meal_name'] = 'Almoço' if time == 2 else 'Jantar'
    boinc_users = boincstats.get_team_users(2068385380)
    boinc_users.sort(key=lambda x: -x['weekly'])
    context['boinc_users'] = boinc_users[:3]
    boinc_projects = boincstats.get_team_projects(2068385380)
    boinc_projects.sort(key=lambda x: -x['weekly'])
    context['boinc_projects'] = boinc_projects[:3]
    departures = cache.get('departures')
    if departures is None:
        departures = list(chain(mts.get_departure_times(), tst.get_departure_times()))
        for departure in departures:
            today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            now = datetime.now().time()
            departure_time = departure['time']
            if now < departure_time:
                departure['datetime'] = today + timedelta(hours=departure_time.hour, minutes=departure_time.minute)
            else:
                departure['datetime'] = today + timedelta(days=1, hours=departure_time.hour,
                                                          minutes=departure_time.minute)
        departures.sort(key=lambda departure: departure['datetime'])
        departures = departures[:5]
        cache.set('departures', departures, timeout=60)
    context['departures'] = departures

    return render(request, 'supernova/index.html', context)


def build_base_context(request):
    result = {
        'disable_auth': False,
        'sub_nav': None,
    }
    if not request.user.is_authenticated:
        result['login_form'] = LoginForm()
    return result
