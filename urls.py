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
    path('grupos/', views.groups, name='groups'),
    path('grupos/<str:group_id>/', views.group, name='group'),
    path('departamentos/', views.departments, name='departments'),
    path('departamento/<str:department_id>/', views.department, name='department'),
    path('departamento/<str:department_id>/cadeira/<str:class_id>/', views.class_view, name='class'),
    path('departamento/<str:department_id>/cadeira/<str:class_id>/instância/<str:year>/<int:period_id>/',
         views.class_instance_view, name='class_instance'),
    path('departamento/<str:department_id>/cadeira/<str:class_id>/instância/<str:year>/<int:period_id>/horário',
         views.class_instance_schedule_view, name='class_instance_schedule'),
    path('entrar/', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),
    path('perfil/<str:nickname>/', views.profile, name='profile'),
    path('perfil/<str:nickname>/agregar', views.profile_crawler, name='profile_crawler'),
    path('perfil/<str:nickname>/definições', views.profile_settings, name='profile_settings'),
    path('criar/', views.create_account, name='create_account'),
    url(r'^captcha/', include('captcha.urls'))
]
