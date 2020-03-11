from django.contrib import admin

from services import models as m
from services import forms as f


class ServiceScheduleInline(admin.TabularInline):
    model = m.ServiceScheduleEntry


class ProductInline(admin.TabularInline):
    model = m.Product


class ServiceAdmin(admin.ModelAdmin):
    form = f.ServiceForm
    inlines = [ServiceScheduleInline, ProductInline]


admin.site.register(m.Service, ServiceAdmin)
admin.site.register(m.Product)
admin.site.register(m.ProductCategory)
