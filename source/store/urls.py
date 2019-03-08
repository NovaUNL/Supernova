from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='all_items'),
    path('artigo/<int:item_id>', views.item, name='item')
]
