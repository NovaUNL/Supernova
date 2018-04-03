from django.contrib import admin

from services.models import Service, MenuDish, Dish, Product, ProductCategory, ServiceProduct

admin.site.register(Service)
admin.site.register(MenuDish)
admin.site.register(Dish)
admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ServiceProduct)
