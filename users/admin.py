from django.contrib import admin

from users.models import Profile, Badge, UserBadges

admin.site.register(Profile)
admin.site.register(Badge)
admin.site.register(UserBadges)
