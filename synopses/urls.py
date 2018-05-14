from django.urls import path

from . import views

app_name = 'synopses'

urlpatterns = [
    path('', views.areas_view, name='areas'),
    path('area/<int:area_id>/', views.area_view, name='area'),
    path('area/<int:area_id>/propor/', views.subarea_create_view, name='subarea_create'),
    path('subarea/<int:subarea_id>/', views.subarea_view, name='subarea'),
    path('subarea/<int:subarea_id>/editar/', views.subarea_edit_view, name='subarea_edit'),
    path('subarea/<int:subarea_id>/criar_topico/', views.topic_create_view, name='topic_create'),
    path('topico/<int:topic_id>/', views.topic_view, name='topic'),
    path('topico/<int:topic_id>/editar/', views.topic_edit_view, name='topic_edit'),
    path('topico/<int:topic_id>/seccoes/', views.topic_manage_sections_view, name='topic_manage'),
    path('topico/<int:topic_id>/<int:section_id>/', views.topic_section_view, name='topic_section'),
    path('topico/<int:topic_id>/criar_seccao/', views.section_create_view, name='section_create'),
    path('topico/<int:topic_id>/<int:section_id>/editar/', views.section_edit_view, name='section_edit'),
    path('cadeira/<int:class_id>/', views.class_sections_view, name='class'),
    path('cadeira/<int:class_id>/seccoes/', views.class_manage_sections_view, name='class_manage'),
    path('cadeira/<int:class_id>/<int:section_id>/', views.class_section_view, name='class_section'),
    path('seccao/<int:section_id>/', views.section_view, name='section'),
    # Autocompletion helpers
    path('ac/area/', views.AreaAutocomplete.as_view(), name='area_ac'),
    path('ac/subarea/', views.SubareaAutocomplete.as_view(), name='subarea_ac'),
    path('ac/topic/', views.TopicAutocomplete.as_view(), name='topic_ac'),
    path('ac/section/', views.SectionAutocomplete.as_view(), name='section_ac'),
]
