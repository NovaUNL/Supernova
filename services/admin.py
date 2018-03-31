from django.contrib import admin

from services.models import Service, Bar, BarDailyMenu, BarPrice

admin.site.register(Service)
admin.site.register(Bar)
admin.site.register(BarDailyMenu)
admin.site.register(BarPrice)
