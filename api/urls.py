from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^profile/(?P<nickname>\w+)/$', views.ProfileDetailed.as_view()),
    url(r'^buildings/$', views.BuildingList.as_view()),
    url(r'^building/(?P<pk>[0-9]+)/$', views.BuildingDetailed.as_view()),
    url(r'^bars/$', views.BarList.as_view()),
    url(r'^services/$', views.ServiceList.as_view()),
    url(r'^departments/$', views.DepartmentList.as_view()),
    url(r'^department/(?P<pk>[0-9]+)/$', views.DepartmentDetailed.as_view()),
    url(r'^course/(?P<pk>[0-9]+)/$', views.CourseDetailed.as_view()),
    url(r'^class/(?P<pk>[0-9]+)/$', views.ClassDetailed.as_view()),
    url(r'^news/$', views.NewsList.as_view()),
    url(r'^news/(?P<pk>[0-9]+)/$', views.News.as_view()),
    # url(r'^articles/$', None),
    url(r'^groups/$', views.GroupList.as_view()),
    url(r'^menus/$', views.Menus.as_view()),
    url(r'^synopsis_areas/$', views.SyopsesAreas.as_view()),
    url(r'^synopsis_topic/(?P<pk>[0-9]+)/$', views.SyopsesTopicSections.as_view()),
    url(r'^store/$', views.Store.as_view()),
    # url(r'^classified/$', None),
    # url(r'^events/$', None),
    url(r'^campus_map/$', views.CampusMap.as_view()),
    url(r'^transportation_map/$', views.TransportationMap.as_view()),
]
