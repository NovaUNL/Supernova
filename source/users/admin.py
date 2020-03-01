from django.contrib import admin
from users import models as m

admin.site.register(m.User)
admin.site.register(m.Badge)
admin.site.register(m.UserBadge)
admin.site.register(m.SocialNetworkAccount)
admin.site.register(m.Registration)
admin.site.register(m.Invite)
