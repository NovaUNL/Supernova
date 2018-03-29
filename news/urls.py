from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('', views.list_view, name='recent'),
    path('<str:news_item_id>/', views.item_view, name='news_item'),
]
