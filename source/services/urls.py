from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('cantina/', views.canteen_view, name='canteen'),
]
