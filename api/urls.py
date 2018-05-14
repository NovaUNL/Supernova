from django.urls import path

from api import views

urlpatterns = [
    path('profile/<str:nickname>/', views.users.ProfileDetailed.as_view()),
    path('profile/<str:nickname>/socialnetworks/', views.users.UserSocialNetworks.as_view(), name='social_networks'),
    path('buildings/', views.college.BuildingList.as_view()),
    path('building/<int:pk>/', views.college.BuildingDetailed.as_view()),
    path('bars/', views.services.BarList.as_view()),
    path('services/', views.services.ServiceList.as_view()),
    path('departments/', views.college.DepartmentList.as_view()),
    path('department/<int:pk>/', views.college.DepartmentDetailed.as_view()),
    path('course/<int:pk>/', views.college.CourseDetailed.as_view()),
    path('class/<int:pk>/', views.college.ClassDetailed.as_view()),
    path('news/', views.news.NewsList.as_view()),
    path('news/<int:pk>/', views.news.News.as_view()),
    path('groups/', views.groups.GroupList.as_view()),
    path('menus/', views.services.Menus.as_view()),
    path('synopses/areas/', views.synopses.SyopsesAreas.as_view()),
    path('synopses/topic/<int:pk>/', views.synopses.SynopsesTopicSections.as_view()),
    path('synopses/class/<int:pk>/', views.synopses.SynopsesClassSections.as_view()),
    path('store/', views.store.Store.as_view()),
    path('campus_map/', views.college.CampusMap.as_view()),
]
