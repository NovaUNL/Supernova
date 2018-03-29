from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.all_items_view, name='all_items'),
    path('artigo/<int:item_id>', views.item_view, name='item')
]
