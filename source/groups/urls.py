from django.urls import path

from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('nucleos', views.nuclei_view, name='nuclei'),
    path('institucional', views.institutional_view, name='institutional'),
    path('pedagogic', views.pedagogic_view, name='pedagogic'),
    path('comunidades', views.communities_view, name='communities'),
    path('<str:group_abbr>/', views.group_view, name='group'),
    path('<str:group_abbr>/documentos/', views.documents_view, name='documents'),
    path('<str:group_abbr>/anuncios/', views.announcements_view, name='announcements'),
    path('anuncio/<str:announcement_id>/', views.announcement_view, name='announcement'),
    path('<str:group_abbr>/contactar/', views.contact_view, name='contact'),
]
