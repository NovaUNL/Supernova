from django.contrib import admin
from users.models import Badge, UserBadge, User, SocialNetworkAccount

admin.site.register(User)
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(SocialNetworkAccount)
