from django.db import models
from django.db.models import Model, TextField, ForeignKey, DateTimeField, ManyToManyField, BooleanField

from kleep.models import KLEEP_TABLE_PREFIX
from users.models import Profile


class GroupType(Model):
    type = TextField(max_length=50)
    description = TextField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_types'

    def __str__(self):
        return self.type


class Role(Model):
    name = TextField(max_length=30)
    is_group_admin = BooleanField(default=False)
    is_group_manager = BooleanField(default=False)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'roles'


class Group(Model):
    abbreviation = TextField(max_length=30, null=True, blank=True)
    name = TextField(max_length=50)
    description = TextField()
    invite_only = BooleanField(default=True)
    type = ForeignKey(GroupType, on_delete=models.PROTECT, null=True, blank=True)
    public_members = BooleanField(default=False)
    members = ManyToManyField(Profile, through='GroupMembers')
    roles = ManyToManyField(Role, through='GroupRoles')
    img_url = TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'groups'

    def __str__(self):
        return self.name


class GroupMembers(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE)
    member = ForeignKey(Profile, on_delete=models.CASCADE)
    role = ForeignKey(Role, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_users'


class GroupRoles(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE)
    role = ForeignKey(Role, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_roles'


class GroupAnnouncement(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE)
    title = TextField(max_length=256)
    announcement = TextField()
    announcer = ForeignKey(Profile, on_delete=models.PROTECT)  # TODO consider user deletion
    datetime = DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_announcement'

    def __str__(self):
        return self.title
