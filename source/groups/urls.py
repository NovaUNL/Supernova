from django.urls import path

from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('nucleos', views.nuclei_view, name='nuclei'),
    path('institucionais', views.institutional_view, name='institutional'),
    path('pedagogicos', views.pedagogic_view, name='pedagogic'),
    path('comunidades', views.communities_view, name='communities'),
    path('<str:group_abbr>/', views.group_view, name='group'),
    path('<str:group_abbr>/documentos/', views.documents_view, name='documents'),
    path('<str:group_abbr>/anuncios/', views.announcements_view, name='announcements'),
    path('<str:group_abbr>/membros/', views.members_view, name='members'),
    path('<str:group_abbr>/cargos/', views.roles_view, name='roles'),
    path('anuncio/<str:announcement_id>/', views.announcement_view, name='announcement'),
    path('<str:group_abbr>/contactar/', views.contact_view, name='contact'),
    path('group_role_ac', views.GroupRolesAutocomplete.as_view(), name='group_role_ac'),
]
