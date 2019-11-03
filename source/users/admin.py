from django.contrib import admin
from users.models import Badge, UserBadge, User, SocialNetworkAccount, Registration

admin.site.register(User)
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(SocialNetworkAccount)
admin.site.register(Registration)
