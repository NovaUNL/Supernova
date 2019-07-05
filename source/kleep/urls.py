from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import college.views as college
import users.views as users
import groups.views as groups
import events.views as events
import feedback.views as feedback
import documents.views as documents
import news.views as news
import api.urls
from settings import DEBUG, MEDIA_URL, MEDIA_ROOT
from . import views

app_name = 'kleep'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Generic views
    path('', views.index, name='index'),
    path('sobre/', views.about, name='about'),
    path('pedinchar/', views.beg, name='beg'),
    path('privacidade/', views.privacy, name='privacy'),
    # College views
    path('faculdade/', include('college.urls')),
    # User views
    path('perfil/<str:nickname>/', users.profile_view, name='profile'),
    path('perfil/<str:nickname>/horario/', users.user_schedule_view, name='profile_schedule'),
    path('perfil/<str:nickname>/agregar/', users.user_clip_crawler_view, name='profile_crawler'),
    path('perfil/<str:nickname>/definicoes/', users.user_profile_settings_view, name='profile_settings'),
    path('perfil/<str:nickname>/social/', users.user_profile_social_view, name='profile_social'),
    path('perfil/<str:nickname>/password/', users.user_profile_password_view, name='profile_password'),
    path('criar/', users.registration_view, name='registration'),
    path('confirmar/', users.registration_validation_view, name='registration_validation'),
    path('entrar/', users.login_view, name='login'),
    path('sair/', users.logout_view, name='logout'),
    # Group views
    path('grupos/', groups.groups_view, name='groups'),
    path('grupo/<str:group_id>/', groups.group_view, name='group'),
    path('grupo/<str:group_id>/documentos/', groups.documents_view, name='group_documents'),
    path('grupo/<str:group_id>/anuncios/', groups.announcements_view, name='group_announcements'),
    path('grupo/anuncio/<str:announcement_id>/', groups.announcement_view, name='group_announcement'),
    path('grupo/<str:group_id>/contactar/', groups.contact_view, name='group_contact'),
    # Events views
    path('eventos/', events.index, name='events'),
    path('evento/<str:event_id>/', events.event, name='event'),
    # Feedback views
    path('feedback/', feedback.feedback_list, name='feedback'),
    path('feedback/<int:idea_id>/', feedback.idea, name='feedback_idea'),
    # Documents views
    path('documento/<int:document_id>/', documents.document, name='document'),
    # News views
    path('noticias/', news.index, name='news_index'),
    path('noticia/<str:news_item_id>/', news.item, name='news_item'),
    # Synopses views
    url(r'^sinteses/', include('synopses.urls')),
    url(r'^exercicios/', include('exercises.urls')),
    url(r'^loja/', include('store.urls')),
    # REST API views
    url(r'^api/', include(api.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
    # Utils
    url(r'^captcha/', include('captcha.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^markdownx/', include('markdownx.urls')),
]
if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
