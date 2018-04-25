from django.db import models
from django.db.models import Model, TextField, ForeignKey, DateTimeField, ManyToManyField, BooleanField, IntegerField, \
    ImageField

from users.models import User


def group_profile_pic_path(group, filename):
    return f'g/{group.id}/pic.{filename.split(".")[-1]}'


class Role(Model):
    name = TextField(max_length=30)
    is_group_admin = BooleanField(default=False)
    is_group_manager = BooleanField(default=False)


class Group(Model):
    abbreviation = TextField(max_length=30, null=True, blank=True)
    name = TextField(max_length=50)
    description = TextField()
    invite_only = BooleanField(default=True)
    public_members = BooleanField(default=False)
    members = ManyToManyField(User, through='GroupMember')
    roles = ManyToManyField(Role, through='GroupRole')
    image = ImageField(upload_to=group_profile_pic_path, null=True, blank=True)

    INSTITUTIONAL = 0
    STUDENTS_ASSOCIATION = 1
    ACADEMIC_ASSOCIATION = 2
    PEDAGOGIC = 3
    PRAXIS = 4

    GROUP_TYPES = (
        (INSTITUTIONAL, 'Intitucional'),
        (STUDENTS_ASSOCIATION, 'Núcleo'),
        (ACADEMIC_ASSOCIATION, 'Associação'),
        (PEDAGOGIC, 'Pedagógico'),
        (PRAXIS, 'CoPe'),
    )

    type = IntegerField(choices=GROUP_TYPES)

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
