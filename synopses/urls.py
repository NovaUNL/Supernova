from django.urls import path

from . import views

app_name = 'synopses'

urlpatterns = [
    path('', views.areas_view, name='areas'),
    path('area/<int:area_id>/', views.area_view, name='area'),
    path('subarea/<int:subarea_id>/', views.subarea_view, name='subarea'),
    path('topico/<int:topic_id>/', views.topic_view, name='topic'),
    path('topico/<int:topic_id>/<int:section_id>/', views.section_view, name='section'),
    path('topico/<int:topic_id>/nova_entrada/', views.section_creation_view, name='create_section'),
    path('topico/<int:topic_id>/<int:section_id>/editar/', views.section_edition_view, name='edit_section'),
]
