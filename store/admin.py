from django.contrib import admin

from store.models import ClassifiedItem, StoreItem

admin.site.register(StoreItem)
admin.site.register(ClassifiedItem)
