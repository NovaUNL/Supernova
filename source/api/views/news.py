from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from api import serializers
from news import models as news


class NewsList(generics.ListAPIView):
    queryset = news.NewsItem.objects.all()
    serializer_class = serializers.news.NewsSerializer


class News(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.news.NewsSerializer(news.NewsItem.objects.get(id=pk))
        return Response(serializer.data)
