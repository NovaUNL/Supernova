from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import api.urls
from kleep import settings
from . import views

app_name = 'kleep'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('departamentos/', views.departments, name='departments'),
    path('departamento/<str:department_id>/', views.department, name='department'),
    path('cadeira/<str:class_id>/', views.class_view, name='class'),
    path('cadeira/<int:class_id>/resumo/', views.class_synopsis, name='class_synopsis'),
    path('cadeira/<int:class_id>/resumo/<int:section_id>/', views.class_synopsis_section,
         name='class_synopsis_section'),
    path('cadeira/i/<int:instance_id>/', views.class_instance_view, name='class_instance'),
    path('cadeira/i/<int:instance_id>/horario', views.class_instance_schedule_view, name='class_instance_schedule'),
    path('cadeira/i/<int:instance_id>/turnos', views.class_instance_turns_view, name='class_instance_turns'),
    path('campus/', views.campus, name='campus'),
    path('campus/transportes/', views.campus_transportation, name='transportation'),
    path('campus/edificio/<str:building_id>/', views.building, name='building'),
    path('campus/edificio/<str:building_id>/servico/<str:service_id>/', views.service, name='service'),
    path('sala/<str:classroom_id>/', views.classroom_view, name='classroom'),
    path('areas/', views.areas, name='areas'),
    path('area/<int:area_id>/', views.area, name='area'),
    path('curso/<int:course_id>/', views.course, name='course'),
    path('curso/<int:course_id>/alunos/', views.course_students, name='course_students'),
    path('curso/<int:course_id>/programa/', views.course_curriculum, name='course_curriculum'),
    path('perfil/<str:nickname>/', views.profile, name='profile'),
    path('perfil/<str:nickname>/horario/', views.profile_schedule, name='profile_schedule'),
    path('perfil/<str:nickname>/agregar/', views.profile_crawler, name='profile_crawler'),
    path('perfil/<str:nickname>/definicoes/', views.profile_settings, name='profile_settings'),
    path('criar/', views.create_account, name='create_account'),
    path('entrar/', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),
    path('eventos/', views.events, name='events'),
    path('evento/<str:event_id>/', views.event, name='event'),
    path('grupos/', views.groups, name='groups'),
    path('grupo/<str:group_id>/', views.group, name='group'),
    path('grupo/<str:group_id>/documentos/', views.group_documents, name='group_documents'),
    path('grupo/<str:group_id>/anuncios/', views.group_announcements, name='group_announcements'),
    path('grupo/anuncio/<str:announcement_id>/', views.group_announcement, name='group_announcement'),
    path('grupo/<str:group_id>/contactar/', views.group_contact, name='group_contact'),
    path('noticias/', views.news, name='news'),
    path('noticia/<str:news_item_id>/', views.news_item, name='news_item'),
    path('resumos/', views.synopsis_areas, name='synopsis_areas'),
    path('resumo/area/<int:area_id>/', views.synopsis_area, name='synopsis_area'),
    path('resumo/subarea/<int:subarea_id>/', views.synopsis_subarea, name='synopsis_subarea'),
    path('resumo/topico/<int:topic_id>/', views.synopsis_topic, name='synopsis_topic'),
    path('resumo/topico/<int:topic_id>/<int:section_id>/', views.synopsis_section, name='synopsis_section'),
    path('resumo/topico/<int:topic_id>/nova_entrada/', views.synopsis_create_section, name='synopsis_create_section'),
    path('resumo/topico/<int:topic_id>/<int:section_id>/editar/', views.synopsis_edit_section,
         name='synopsis_edit_section'),
    path('artigos/', views.articles, name='articles'),
    path('artigo/<int:article_id>', views.article_item, name='article_item'),
    path('ementas/', views.lunch, name='lunch'),
    path('loja/', views.store, name='store'),
    path('loja/artigo/<int:item_id>', views.store_item, name='store_item'),
    path('classificados/', views.classified_items, name='classified'),
    path('classificados/<int:item_id>', views.classified_item, name='classified_item'),
    path('feedback/', views.feedback, name='feedback'),
    path('feedback/<int:idea_id>/', views.feedback_idea, name='feedback_idea'),
    path('sobre/', views.about, name='about'),
    path('pedinchar/', views.beg, name='beg'),
    path('privacidade/', views.privacy, name='privacy'),
    path('documento/<int:document_id>/', views.document, name='document'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^api/', include(api.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
