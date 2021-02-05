from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('', views.services_view, name='services'),
    path('<str:service_abbr>/', views.service_view, name='service'),
]
