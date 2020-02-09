from rest_framework.decorators import api_view
from rest_framework.response import Response

from scrapper.git import gitlab, github
from scrapper.weather.ipma import get_weather
from scrapper.boinc import boincstats


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
def gitlab_stars(request):
    response = gitlab.get_repo_stars()
    return Response(response)


@api_view(['GET'])
def github_stars(request):
    response = github.get_repo_stars()
    return Response(response)
