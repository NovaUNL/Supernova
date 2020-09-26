from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('<str:nickname>/', views.profile_view, name='profile'),
    path('<str:nickname>/horario/', views.user_schedule_view, name='schedule'),
    path('<str:nickname>/calendario/', views.user_calendar_view, name='calendar'),
    path('<str:nickname>/calendario/editar', views.user_calendar_management_view, name='calendar_manage'),
    path('<str:nickname>/reputacao/', views.user_reputation_view, name='reputation'),
    path('<str:nickname>/definicoes/', views.user_profile_settings_view, name='settings'),
    path('<str:nickname>/convites/', views.invites_view, name='invites'),
    path('<str:nickname>/convites/novo', views.create_invite_view, name='create_invite'),
    path('notificacoes', views.notifications_view, name='notifications'),
    path('ac/nickname/', views.NicknameAutocomplete.as_view(), name='nickname_ac'),
]
