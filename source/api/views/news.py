from rest_framework.response import Response
from rest_framework.views import APIView

from api import serializers
from news import models as news


class NewsList(APIView):
    def get(self, request, format=None):
        serializer = serializers.news.NewsMinimalSerializer(news.NewsItem.objects.all(), many=True)
        return Response(serializer.data)


class News(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.news.NewsSerializer(news.NewsItem.objects.get(id=pk))
        return Response(serializer.data)
