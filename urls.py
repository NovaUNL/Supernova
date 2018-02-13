from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'kleep'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('beg/', views.beg, name='beg'),
    path('privacy/', views.privacy, name='privacy'),
    path('campus/', views.campus, name='campus'),
    # path('campus/transportation/', views.campus, name='transportation'),
    # path('campus/building/<str:building_id>/', views.building, name='building'),
    # path('campus/service/<str:service_id>/', views.building, name='service'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('create/', views.create_account, name='create_account'),
    url(r'^captcha/', include('captcha.urls'))
]
