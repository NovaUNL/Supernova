from itertools import chain
from datetime import datetime, timedelta

from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response

from scrapper.git import gitlab, github
from scrapper.transportation import mts, tst
from scrapper.weather.ipma import get_weather
from scrapper.boinc import boincstats


@api_view(['GET'])
def transportation_upcoming(request):
    departures = cache.get('departures')
    if departures is None:
        try:
            now = datetime.now()
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            departures = list(chain(mts.get_departure_times(), tst.get_departure_times()))
            curr_time = now.time()
            for departure in departures:
                departure_time = departure['time']
                if curr_time < departure_time:
                    departure['datetime'] = midnight + timedelta(
                        hours=departure_time.hour, minutes=departure_time.minute)
                else:
                    departure['datetime'] = midnight + timedelta(
                        days=1, hours=departure_time.hour, minutes=departure_time.minute)
            departures.sort(key=lambda departure: departure['datetime'])
            departures = departures[:5]
            cache.set('departures', departures, timeout=60 * 10)
        except Exception:
            departures = []
    return Response(departures)


@api_view(['GET'])
def weather(request):
    return Response(get_weather())


@api_view(['GET'])
def weather_chart(request):
    weather = get_weather()
    if 'hours' in weather:
        return Response(weather['hours'])

    return Response({'error': 'unable to fetch the weather at this time'})


@api_view(['GET'])
def boinc_users(request):
    response = boincstats.get_team_users(2068385380)
    return Response(response)


@api_view(['GET'])
def boinc_projects(request):
    response = boincstats.get_team_projects(2068385380)
    return Response(response)


@api_view(['GET'])
@cache_page(3600)
def github_stars(request):
    response = github.get_repo_stars()
    return Response(response)


@api_view(['GET'])
@cache_page(3600)
def gitlab_stars(request):
    response = gitlab.get_repo_stars()
    return Response(response)
