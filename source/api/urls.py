from django.urls import path

from api import views

app_name = 'api'

urlpatterns = [
    # College
    path('buildings/', views.college.BuildingList.as_view(), name="buildings"),
    path('building/<int:pk>/', views.college.BuildingDetailed.as_view(), name="building"),
    path('departments/', views.college.DepartmentList.as_view(), name="departments"),
    path('department/<int:pk>/', views.college.DepartmentDetailed.as_view(), name="department"),
    path('course/<int:pk>/', views.college.CourseDetailed.as_view(), name="course"),
    path('class/<int:pk>/', views.college.ClassDetailed.as_view(), name="class"),
    # Chat
    # path('chat/list', views.chat.chat_list, name='chat_list'),
    path('chat/presence', views.chat.chat_presence, name='chat_presence'),
    path('chat/query', views.chat.chat_query, name='chat_query'),
    path('chat/<int:chat_id>/info', views.chat.chat_info, name='chat_info'),
    path('chat/<str:reference>/join', views.chat.chat_join_request, name='chat_join'),
    path('chat/<int:chat_id>/history', views.chat.chat_history, name='chat_history'),
    path('chat/<int:user_id>/dmrequest', views.chat.dm_request, name='chat_dm_request'),
    # Groups
    path('groups/', views.groups.GroupList.as_view(), name="groups"),
    path('groups/<str:abbr>/schedule/<str:from_date>/<str:to_date>', views.groups.group_schedule,
         name='group_schedule'),
    path('group/<str:abbr>/subscribe', views.groups.GroupSubscription.as_view(), name='group_subscription'),
    path('group/<str:abbr>/subscribe', views.groups.GroupMembershipRequest.as_view(), name='group_membership_request'),
    # News
    path('news/', views.news.NewsList.as_view(), name="news"),
    path('news/<int:pk>/', views.news.News.as_view(), name="news_item"),
    # Services
    path('services/', views.services.ServiceList.as_view(), name="services"),
    path('bars/', views.services.BarList.as_view(), name="services_bars"),
    path('transportation/next', views.third_party.transportation_upcoming, name="transportation_upcoming"),
    path('weather/', views.third_party.weather, name="weather"),
    path('weather/chart/', views.third_party.weather_chart, name="weather_chart"),
    path('boinc/users/', views.third_party.boinc_users, name="boinc_users"),
    path('boinc/projects/', views.third_party.boinc_projects, name="boinc_projects"),
    path('stars/gitlab/', views.third_party.gitlab_stars, name="gitlab_stars"),
    path('stars/github/', views.third_party.github_stars, name="github_stars"),
    # Store
    path('store/', views.store.Store.as_view(), name="store"),
    # Synopses
    path('learning/areas/', views.learning.Areas.as_view(), name="synopses_areas"),
    path('learning/area/<int:pk>/', views.learning.Area.as_view(), name="synopses_area"),
    path('learning/subarea/<int:pk>/', views.learning.Subarea.as_view(), name="synopses_subarea"),
    path('learning/class/<int:pk>/children/', views.learning.ClassSections.as_view(),
         name='synopses_class_section'),
    path('learning/section/<int:pk>/', views.learning.Section.as_view(), name="synopses_section"),
    path('learning/section/<int:pk>/children/', views.learning.SectionChildren.as_view(),
         name='synopses_section_children'),
    path('learning/postable/<int:pk>/votes', views.learning.PostableVotes.as_view(), name="postable_votes"),
    path('learning/question/<int:pk>/votes', views.learning.QuestionUserVotes.as_view(), name="question_votes"),
    # Users
    path('profile/<str:nickname>/', views.users.ProfileDetailed.as_view(), name="user_profile"),
    path('profile/<str:nickname>/socialnetworks/', views.users.UserSocialNetworks.as_view(), name='social_networks'),
    path('user/<str:nickname>/current_shifts', views.college.UserShiftInstances.as_view()),
    path('user/<str:nickname>/schedule/<str:from_date>/<str:to_date>', views.users.user_schedule, name='user_schedule'),
    path('notification/count', views.users.notification_count_view, name='notification_count'),
    path('notification/list', views.users.UserNotificationList.as_view(), name='notification_list'),
    path('moderate/<int:user_id>/', views.users.UserModeration.as_view(), name='user_moderation'),
]
