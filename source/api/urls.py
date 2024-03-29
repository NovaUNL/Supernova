from django.urls import path

from api import views

app_name = 'api'

urlpatterns = [
    path('search', views.search.search_view, name="search"),
    # College
    path('buildings', views.college.BuildingList.as_view(), name="buildings"),
    path('places', views.college.PlaceList.as_view(), name="places"),
    path('rooms', views.college.RoomList.as_view(), name="rooms"),
    path('building/<int:building_id>/', views.college.Building.as_view(), name="building"),
    path('building/<int:building_id>/rooms', views.calendar.building_schedule_rooms_view,
         name="building_schedule_rooms"),
    path('building/<int:building_id>/schedule', views.calendar.building_schedule_shifts_view, name="building_schedule"),
    path('departments', views.college.DepartmentList.as_view(), name="departments"),
    path('department/<int:department_id>/', views.college.DepartmentDetailed.as_view(), name="department"),
    path('classes', views.college.ClassList.as_view(), name="classes"),
    path('courses', views.college.CoursesList.as_view(), name="courses"),
    path('course/<int:course_id>/', views.college.CourseDetailed.as_view(), name="course"),
    path('class/<int:class_id>/', views.college.Class.as_view(), name="class"),
    path('class/i/<int:instance_id>/', views.college.ClassInstance.as_view(), name="class_instance"),
    path('class/i/<int:instance_id>/shifts', views.college.ClassInstanceShifts.as_view(),
         name="class_instance_shifts"),
    path('class/i/<int:instance_id>/files', views.college.ClassFiles.as_view(), name="class_instance_files"),
    path('class/i/<int:instance_id>/schedule', views.calendar.class_instance_schedule, name="class_instance_schedule"),
    path('shift/<int:shift_id>', views.college.Shift.as_view(), name="shift"),
    path('enrollment/<int:enrollment_id>', views.college.Enrollment.as_view(), name="enrollment"),
    path('teacher/<int:teacher_id>/', views.college.Teacher.as_view(), name="teacher"),
    path('student/<int:student_id>/', views.college.Student.as_view(), name="student"),
    path('teacher/<int:teacher_id>/schedule', views.calendar.teacher_schedule, name="teacher_schedule"),

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
    path('group/<int:group_id>/', views.groups.Group.as_view(), name="group_activities"),
    path('group/<str:abbr>/calendar', views.calendar.group_calendar, name='group_calendar'),
    path('group/<str:abbr>/subscribe', views.groups.GroupSubscription.as_view(), name='group_subscription'),
    path('group/<str:abbr>/membership', views.groups.GroupMembershipRequest.as_view(), name='group_membership_request'),
    # News
    path('news/', views.news.NewsList.as_view(), name="news"),
    path('news/<int:pk>/', views.news.News.as_view(), name="news_item"),
    # Services
    path('services/', views.services.ServiceList.as_view(), name="services"),
    path('bars/', views.services.BarList.as_view(), name="services_bars"),
    path('transportation/day', views.third_party.transportation_day, name="transportation_day"),
    path('transportation/next', views.third_party.transportation_upcoming, name="transportation_upcoming"),
    path('weather/', views.third_party.weather, name="weather"),
    path('weather/chart/', views.third_party.weather_chart, name="weather_chart"),
    path('boinc/', views.third_party.boinc_view, name="boinc"),
    path('boinc/users/', views.third_party.boinc_users, name="boinc_users"),
    path('boinc/projects/', views.third_party.boinc_projects, name="boinc_projects"),
    path('stars/gitlab/', views.third_party.gitlab_stars, name="gitlab_stars"),
    path('stars/github/', views.third_party.github_stars, name="github_stars"),
    # Synopses
    path('learning/areas', views.learning.Areas.as_view(), name="synopses_areas"),
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
    path('login', views.users.Login.as_view(), name="user_login"),
    path('logout', views.users.Logout.as_view(), name="user_logout"),
    path('validation', views.users.ValidateToken.as_view(), name="user_validate"),
    path('profile/<str:nickname>/', views.users.ProfileDetailed.as_view(), name="user_profile"),
    path('profile/<str:nickname>/external_pages', views.users.UserExternalPages.as_view(), name='user_external_pages'),
    path('user/<str:nickname>/current_shifts', views.college.UserShiftInstances.as_view()),
    path('user/<str:nickname>/calendar', views.calendar.user_calendar, name='user_calendar'),
    path('user/<str:nickname>/schedule', views.calendar.user_schedule, name='user_schedule'),
    path('notification/count', views.users.notification_count_view, name='notification_count'),
    path('notification/list', views.users.UserNotificationList.as_view(), name='notification_list'),
    path('moderate/<int:user_id>/', views.users.UserModeration.as_view(), name='user_moderation'),
]
