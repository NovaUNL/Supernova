from django.urls import path

from . import views

app_name = 'feedback'

urlpatterns = [
    path('sugestoes', views.suggestion_index_view, name='index'),
    path('sugestao/criar', views.suggestion_create_view, name='suggestion_create'),
    path('sugestao/criar/<int:content_type_id>/<int:object_id>',
         views.suggestion_create_view,
         name='suggestion_to_create'),
    path('sugestao/<int:suggestion_id>', views.suggestion_view, name='suggestion'),
    path('avaliação', views.review_create_view, name='review_create'),
]
