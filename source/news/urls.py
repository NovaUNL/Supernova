from django.contrib.sitemaps import Sitemap
from django.urls import path

from news import views
from news import models as m

app_name = 'news'


class NewsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return m.NewsItem.objects.filter()

    def lastmod(self, obj):
        return obj.edit_datetime if obj.edited else obj.datetime


urlpatterns = [
    path('', views.index_view, name='index'),
    path('aviso/<str:pinned_item_id>/', views.pinned_item_view, name='pinned_item'),
    path('<str:news_item_id>/', views.item_view, name='item'),
]
