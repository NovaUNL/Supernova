from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup

from groups.models import Type, Role, Group, GroupMember, GroupRole, Announcement

admin.site.unregister(DjangoGroup)

admin.site.register(Type)
admin.site.register(Role)
admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(GroupRole)
admin.site.register(Announcement)
