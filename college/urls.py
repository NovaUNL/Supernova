from django.urls import path

from . import views

app_name = 'college'

urlpatterns = [
    path('campus/', views.campus, name='campus'),
    path('campus/mapa/', views.map, name='map'),
    path('campus/transportes/', views.transportation, name='transportation'),
    path('campus/disponivel/', views.available_places, name='available_places'),
    path('campus/edificio/<int:building_id>/', views.building, name='building'),
    path('campus/servico/<int:service_id>/', views.service, name='service'),
    path('departamentos/', views.departments, name='departments'),
    path('departamento/<int:department_id>/', views.department, name='department'),
    path('cadeira/<int:class_id>/', views.class_view, name='class'),
    # path('cadeira/<int:class_id>/resumo/', #, name='class_synopsis'),
    # path('cadeira/<int:class_id>/resumo/<int:section_id>/', #, name='class_synopsis_section'),
    path('cadeira/i/<int:instance_id>/', views.class_instance, name='class_instance'),
    path('cadeira/i/<int:instance_id>/horario', views.class_instance_schedule, name='class_instance_schedule'),
    path('cadeira/i/<int:instance_id>/turnos', views.class_instance_turns, name='class_instance_turns'),
    path('sala/<int:room_id>/', views.room, name='room'),
    path('areas/', views.areas, name='areas'),
    path('area/<int:area_id>/', views.area, name='area'),
    path('curso/<int:course_id>/', views.course, name='course'),
    path('curso/<int:course_id>/alunos/', views.course_students, name='course_students'),
    path('curso/<int:course_id>/programa/', views.course_curriculum, name='course_curriculum'),
    path('ac/class/', views.ClassAutocomplete.as_view(), name='class_ac'),
]
