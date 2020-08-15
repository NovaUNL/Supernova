from django.urls import path

from . import views

app_name = 'exercises'

urlpatterns = [
    path('', views.index, name='index'),
    path('criar/', views.create_exercise, name='create'),
]
