from rest_framework.decorators import api_view
from rest_framework.response import Response

from scrapper.weather.ipma import get_weather


@api_view(['GET'])
def weather(request):
    return Response(get_weather())


@api_view(['GET'])
def weather_chart(request):
    return Response(get_weather()['hours'])
