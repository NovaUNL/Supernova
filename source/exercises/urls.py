from django.urls import path

from . import views

app_name = 'exercises'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('criar/', views.create_exercise_view, name='create'),
    path('editar/<int:exercise_id>/', views.edit_exercise_view, name='edit'),
    path('<int:exercise_id>/', views.exercise_view, name='exercise'),
]
