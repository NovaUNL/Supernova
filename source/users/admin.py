from django.contrib import admin
from users import models as m
from users import forms as f


class UserAdmin(admin.ModelAdmin):
    form = f.UserForm


admin.site.register(m.User, UserAdmin)
admin.site.register(m.Badge)
admin.site.register(m.UserBadge)
admin.site.register(m.SocialNetworkAccount)
admin.site.register(m.Registration)
admin.site.register(m.Invite)
