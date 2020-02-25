from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('<str:nickname>/', views.profile_view, name='profile'),
    path('<str:nickname>/horario/', views.user_schedule_view, name='schedule'),
    path('<str:nickname>/definicoes/', views.user_profile_settings_view, name='settings'),
    path('nickname_ac', views.NicknameAutocomplete.as_view(), name='nickname_ac'),
]
