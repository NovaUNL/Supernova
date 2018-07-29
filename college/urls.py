from django.urls import path

from . import views

app_name = 'college'

urlpatterns = [
    path('campus/', views.campus_view, name='campus'),
    path('campus/mapa/', views.map_view, name='map'),
    path('campus/transportes/', views.transportation_view, name='transportation'),
    path('campus/disponivel/', views.available_places_view, name='available_places'),
    path('campus/edificio/<int:building_id>/', views.building_view, name='building'),
    path('campus/servico/<int:service_id>/', views.service_view, name='service'),
    path('departamentos/', views.departments_view, name='departments'),
    path('departamento/<int:department_id>/', views.department_view, name='department'),
    path('cadeira/<int:class_id>/', views.class_view, name='class'),
    # path('cadeira/<int:class_id>/resumo/', #, name='class_synopsis'),
    # path('cadeira/<int:class_id>/resumo/<int:section_id>/', #, name='class_synopsis_section'),
    path('cadeira/i/<int:instance_id>/', views.class_instance_view, name='class_instance'),
    path('cadeira/i/<int:instance_id>/horario', views.class_instance_schedule_view, name='class_instance_schedule'),
    path('cadeira/i/<int:instance_id>/turnos', views.class_instance_turns_view, name='class_instance_turns'),
    path('sala/<int:room_id>/', views.room_view, name='room'),
    path('areas/', views.areas_view, name='areas'),
    path('area/<int:area_id>/', views.area_view, name='area'),
    path('curso/<int:course_id>/', views.course_view, name='course'),
    path('curso/<int:course_id>/alunos/', views.course_students_view, name='course_students'),
    path('curso/<int:course_id>/programa/', views.course_curriculum_view, name='course_curriculum'),
    path('ac/class/', views.ClassAutocomplete.as_view(), name='class_ac'),
]
