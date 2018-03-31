from django.contrib import admin

from groups.models import GroupType, Role, Group, GroupMembers, GroupRoles, GroupAnnouncement

admin.site.register(GroupType)
admin.site.register(Role)
admin.site.register(Group)
admin.site.register(GroupMembers)
admin.site.register(GroupRoles)
admin.site.register(GroupAnnouncement)
