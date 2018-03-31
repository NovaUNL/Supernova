from django.contrib import admin

from users.models import Profile, Badge, UserBadge

admin.site.register(Profile)
admin.site.register(Badge)
admin.site.register(UserBadge)
