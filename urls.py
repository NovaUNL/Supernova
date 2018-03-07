from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from kleep import settings
from . import views

app_name = 'kleep'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('campus/', views.campus, name='campus'),
    path('campus/transportes/', views.campus_transportation, name='transportation'),
    path('campus/edificio/<str:building_id>/', views.building, name='building'),
    path('campus/edificio/<str:building_id>/servico/<str:service_id>/', views.service, name='service'),
    path('sala/<str:classroom_id>/', views.classroom_view, name='classroom'),
    path('departamentos/', views.departments, name='departments'),
    path('departamento/<str:department_id>/', views.department, name='department'),
    path('cadeira/<str:class_id>/', views.class_view, name='class'),
    path('cadeira/i/<int:instance_id>/', views.class_instance_view, name='class_instance'),
    path('cadeira/i/<int:instance_id>/horario', views.class_instance_schedule_view, name='class_instance_schedule'),
    path('cadeira/i/<int:instance_id>/turnos', views.class_instance_turns_view, name='class_instance_turns'),
    path('areas/', views.areas, name='areas'),
    path('area/<int:area_id>/', views.area, name='area'),
    path('curso/<int:course_id>/', views.course, name='course'),
    path('curso/<int:course_id>/alunos/', views.course_students, name='course_students'),
    path('curso/<int:course_id>/programa/', views.course_curriculum, name='course_curriculum'),
    path('perfil/<str:nickname>/', views.profile, name='profile'),
    path('perfil/<str:nickname>/horario/', views.profile_schedule, name='profile_schedule'),
    path('perfil/<str:nickname>/agregar/', views.profile_crawler, name='profile_crawler'),
    path('perfil/<str:nickname>/definicoes/', views.profile_settings, name='profile_settings'),
    path('grupos/', views.groups, name='groups'),
    path('grupos/<str:group_id>/', views.group, name='group'),
    path('noticias/', views.news, name='news'),
    path('noticia/<str:news_item_id>/', views.news_item, name='news_item'),
    path('eventos/', views.events, name='events'),
    path('evento/<str:event_id>/', views.event, name='event'),
    path('criar/', views.create_account, name='create_account'),
    path('entrar/', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),
    path('sobre/', views.about, name='about'),
    path('pedinchar/', views.beg, name='beg'),
    path('privacidade/', views.privacy, name='privacy'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
