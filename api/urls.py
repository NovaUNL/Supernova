from django.urls import path

from api import views

urlpatterns = [
    path('profile/<str:nickname>/', views.ProfileDetailed.as_view()),
    path('profile/<str:nickname>/socialnetworks/', views.UserSocialNetworks.as_view(), name='social_networks'),
    path('buildings/', views.BuildingList.as_view()),
    path('building/<int:pk>/', views.BuildingDetailed.as_view()),
    path('bars/', views.BarList.as_view()),
    path('services/', views.ServiceList.as_view()),
    path('departments/', views.DepartmentList.as_view()),
    path('department/<int:pk>/', views.DepartmentDetailed.as_view()),
    path('course/<int:pk>/', views.CourseDetailed.as_view()),
    path('class/<int:pk>/', views.ClassDetailed.as_view()),
    path('news/', views.NewsList.as_view()),
    path('news/<int:pk>/', views.News.as_view()),
    path('groups/', views.GroupList.as_view()),
    path('menus/', views.Menus.as_view()),
    path('synopses/areas/', views.SyopsesAreas.as_view()),
    path('synopses/topic/<int:pk>/', views.SynopsesTopicSections.as_view()),
    path('synopses/class/<int:pk>/', views.SynopsesClassSections.as_view()),
    path('store/', views.Store.as_view()),
    path('campus_map/', views.CampusMap.as_view()),
]
