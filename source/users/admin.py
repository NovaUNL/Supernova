from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import Badge, UserBadge, User

admin.site.register(User, UserAdmin)
admin.site.register(Badge)
admin.site.register(UserBadge)
