from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('users/', views.users_view, name='users'),
    path('activity/', views.activity_view, name='activity'),
    path('announcements/', views.announcements_view, name='announcements'),
    path('settings/', views.settings_view, name='settings'),
]
