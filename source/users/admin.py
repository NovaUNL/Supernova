from django.contrib import admin
from users import models as m
from users import forms as f


class UserAdmin(admin.ModelAdmin):
    form = f.UserForm


admin.site.register(m.User, UserAdmin)
admin.site.register(m.Award)
admin.site.register(m.UserAward)
admin.site.register(m.ExternalPage)
admin.site.register(m.Registration)
admin.site.register(m.Invite)
