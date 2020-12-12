from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response

from college.utils import get_transportation_departures
from scrapper.git import gitlab, github
from scrapper.weather.ipma import get_weather
from scrapper.boinc import boincstats


@api_view(['GET'])
def transportation_upcoming(request):
    departures = get_transportation_departures()
    if len(departures) > 5:
        departures = departures[:5]
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
def boinc_view(request):
    users = boincstats.get_team_users(2068385380)
    projects = boincstats.get_team_projects(2068385380)
    return Response({'users': users, 'projects': projects})


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
