import debug_toolbar
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin, sitemaps
from django.contrib.flatpages import views as flatpages
from django.contrib.sitemaps import views as sitemaps_views
from django.views.decorators.cache import cache_page
from django.urls import path, include, reverse
from django.conf import settings

import users.views as users
import documents.views as documents
from news.urls import NewsSitemap
from . import views

app_name = 'supernova'
handler400 = views.bad_request_view
handler403 = views.permission_denied_view
handler404 = views.page_not_found_view
handler500 = views.error_view


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['index', 'about', 'privacy', 'faq', 'terms']

    def location(self, item):
        return reverse(item)


sitemaps = {
    'static': StaticViewSitemap,
    'news': NewsSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    # Generic views
    path('', views.index, name='index'),
    path('alterações', views.changelog_view, name='changelog'),
    path('apoio', views.support_view, name='support'),
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
    # Feedback views
    path('feedback/', include('feedback.urls')),
    # Documents views
    path('documento/<int:document_id>/', documents.document, name='document'),
    # News views
    path('noticias/', include('news.urls')),
    # Learning views
    path('estudo/', include('learning.urls')),
    # Chat views
    path('chat/', include('chat.urls')),
    # Management view
    path('manage/', include('management.urls')),
    # path('loja/', include('store.urls')),
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
    path('intro/', flatpages.flatpage, {'url': '/intro/'}, name='intro'),
    url('', include('pwa.urls')),
    path('sitemap.xml',
         cache_page(86400)(sitemaps_views.index),
         {'sitemaps': sitemaps}),
    path('sitemap-<section>.xml',
         cache_page(86400)(sitemaps_views.sitemap), {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
