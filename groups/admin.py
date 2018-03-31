from django.contrib import admin

from groups.models import GroupType, Role, Group, GroupMember, GroupRole, Announcement

admin.site.register(GroupType)
admin.site.register(Role)
admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(GroupRole)
admin.site.register(Announcement)
