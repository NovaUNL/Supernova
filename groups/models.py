from django.db import models
from django.db.models import Model, TextField, ForeignKey, DateTimeField, ManyToManyField, BooleanField

from users.models import User


class GroupType(Model):
    type = TextField(max_length=50)
    description = TextField()

    def __str__(self):
        return self.type


class Role(Model):
    name = TextField(max_length=30)
    is_group_admin = BooleanField(default=False)
    is_group_manager = BooleanField(default=False)


class Group(Model):
    abbreviation = TextField(max_length=30, null=True, blank=True)
    name = TextField(max_length=50)
    description = TextField()
    invite_only = BooleanField(default=True)
    type = ForeignKey(GroupType, on_delete=models.PROTECT, null=True, blank=True)
    public_members = BooleanField(default=False)
    members = ManyToManyField(User, through='GroupMember')
    roles = ManyToManyField(Role, through='GroupRole')
    img_url = TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class GroupMember(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE)
    member = ForeignKey(User, on_delete=models.CASCADE)
    role = ForeignKey(Role, on_delete=models.PROTECT)


class GroupRole(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE)
    role = ForeignKey(Role, on_delete=models.PROTECT)


class Announcement(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE)
    title = TextField(max_length=256)
    announcement = TextField()
    announcer = ForeignKey(User, on_delete=models.PROTECT)  # TODO consider user deletion
    datetime = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
