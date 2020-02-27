from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup

from groups import models as m

admin.site.unregister(DjangoGroup)
admin.site.register(m.Role)
admin.site.register(m.Group)
admin.site.register(m.Membership)
admin.site.register(m.Announcement)
