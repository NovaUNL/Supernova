from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('', views.index, name='recent'),
    path('<str:news_item_id>/', views.item, name='news_item'),
]
