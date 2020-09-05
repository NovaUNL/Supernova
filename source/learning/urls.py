from django.urls import path

from . import views

app_name = 'learning'

urlpatterns = [
    path('', views.areas_view, name='areas'),
    path('area/<int:area_id>/', views.area_view, name='area'),
    path('area/<int:area_id>/propor/', views.subarea_create_view, name='subarea_create'),
    path('subarea/<int:subarea_id>/', views.subarea_view, name='subarea'),
    path('subarea/<int:subarea_id>/editar/', views.subarea_edit_view, name='subarea_edit'),
    path('subarea/<int:subarea_id>/criar_seccao/', views.subarea_section_create_view, name='subarea_section_create'),
    path('subarea/<int:subarea_id>/seccao/<int:section_id>/', views.subarea_section_view, name='subarea_section'),
    path('seccao/<int:section_id>/', views.section_view, name='section'),
    path('seccao/<int:parent_id>/subseccao/<int:child_id>/', views.subsection_view, name='subsection'),
    path('seccao/<int:section_id>/criar_seccao/', views.subsection_create_view, name='subsection_create'),
    path('seccao/<int:section_id>/autores/', views.section_authors_view, name='section_authors'),
    path('seccao/<int:section_id>/exercicios/', views.section_exercises_view, name='section_exercises'),
    path('cadeira/<int:class_id>/', views.class_sections_view, name='class'),
    path('cadeira/<int:class_id>/seccoes/', views.class_manage_sections_view, name='class_manage'),
    path('cadeira/<int:class_id>/<int:section_id>/', views.class_section_view, name='class_section'),
    path('seccao/<int:section_id>/criar_seccao/', views.section_create_view, name='section_create'),
    path('seccao/<int:section_id>/editar/', views.section_edit_view, name='section_edit'),
    path('exercicios', views.index_view, name='exercises'),
    path('exercicios/criar/', views.create_exercise_view, name='create'),
    path('exercicios/editar/<int:exercise_id>/', views.edit_exercise_view, name='edit'),
    path('exercicios/<int:exercise_id>/', views.exercise_view, name='exercise'),
    # Autocompletion helpers
    path('ac/area/', views.AreaAutocomplete.as_view(), name='area_ac'),
    path('ac/subarea/', views.SubareaAutocomplete.as_view(), name='subarea_ac'),
    path('ac/section/', views.SectionAutocomplete.as_view(), name='section_ac'),
]
