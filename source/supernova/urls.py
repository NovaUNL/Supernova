import debug_toolbar
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views as flatpages
from django.urls import path, include

import users.views as users
import events.views as events
import feedback.views as feedback
import documents.views as documents
import news.views as news
from settings import DEBUG, MEDIA_URL, MEDIA_ROOT
from . import views

app_name = 'supernova'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Generic views
    path('', views.index, name='index'),
    # College views
    path('faculdade/', include('college.urls')),
    # Services views
    path('servicos/', include('services.urls')),
    # User views
    path('u/', include('users.urls')),
    path('criar/', users.registration_view, name='registration'),
    path('confirmar/', users.registration_validation_view, name='registration_validation'),
    path('entrar/', users.login_view, name='login'),
    path('sair/', users.logout_view, name='logout'),
    # Group views
    path('grupos/', include('groups.urls')),
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
    path('sinteses/', include('synopses.urls')),
    path('exercicios/', include('exercises.urls')),
    path('loja/', include('store.urls')),
    # REST API views
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    # Utils
    url(r'^captcha/', include('captcha.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^markdownx/', include('markdownx.urls')),
    path('sobre/', flatpages.flatpage, {'url': '/sobre/'}, name='about'),
    path('privacidade/', flatpages.flatpage, {'url': '/privacidade/'}, name='privacy'),
    path('faq/', flatpages.flatpage, {'url': '/faq/'}, name='faq'),
    path('termos/', flatpages.flatpage, {'url': '/termos/'}, name='terms'),
]

if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
