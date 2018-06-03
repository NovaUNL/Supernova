from django.urls import path

from . import views

app_name = 'exercises'

urlpatterns = [
    path('novo/', views.create_exercise, name='create_exercise'),
    path('novo/simples', views.create_qa_exercise, name='create_qa_exercise'),
    path('novo/escolha_multipla', views.create_multiple_choice_exercise, name='create_multiple_choice_exercise'),
]
