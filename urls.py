from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'kleep'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('sobre/', views.about, name='about'),
    path('pedinchar/', views.beg, name='beg'),
    path('privacidade/', views.privacy, name='privacy'),
    path('campus/', views.campus, name='campus'),
    path('campus/transportes/', views.campus_transportation, name='transportation'),
    path('campus/edifício/<str:building_id>/', views.building, name='building'),
    path('campus/edifício/<str:building_id>/serviço/<str:service_id>/', views.service, name='service'),
    path('entrar/', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),
    path('perfil/<str:nickname>/', views.profile, name='profile'),
    path('perfil/<str:nickname>/agregar', views.profile_crawler, name='profile_crawler'),
    path('perfil/<str:nickname>/definições', views.profile_settings, name='profile_settings'),
    path('criar/', views.create_account, name='create_account'),
    url(r'^captcha/', include('captcha.urls'))
]
