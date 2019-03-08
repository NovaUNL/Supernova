from django.db import models
from django.db.models import Model, TextField, ForeignKey, DateTimeField, ManyToManyField, BooleanField, IntegerField, \
    ImageField

from college.models import Place
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
    members = ManyToManyField(User, through='GroupMember')
    roles = ManyToManyField(Role, through='GroupRole')
    place = ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True)
    image = ImageField(upload_to=group_profile_pic_path, null=True, blank=True)

    INSTITUTIONAL = 0
    STUDENTS_ASSOCIATION = 1
    ACADEMIC_ASSOCIATION = 2
    PEDAGOGIC = 3
    PRAXIS = 4
    COMMUNITY = 5

    GROUP_TYPES = (
        (INSTITUTIONAL, 'Intitucional'),
        (STUDENTS_ASSOCIATION, 'Núcleo'),
        (ACADEMIC_ASSOCIATION, 'Associação'),
        (PEDAGOGIC, 'Pedagógico'),
        (PRAXIS, 'CoPe'),
        (COMMUNITY, 'Comunidade'),
    )

    type = IntegerField(choices=GROUP_TYPES)

    SECRET = 0  # The group is invisible
    CLOSED = 1  # The group is visible but closed to join and invitations have to be sent by group members
    CLOSED_PRIVATE = 2  # Same as CLOSED, but by default only members can see what happens
    REQUEST = 3  # The group is visible and closed to join, but users can request to become members
    REQUEST_PRIVATE = 4  # Same as REQUEST, but by default only members can see what happens
    OPEN = 5  # Anyone can join the group freely without authorization.

    NON_MEMBER_PERMISSION_CHOICES = (
        (SECRET, 'Secreto'),
        (CLOSED, 'Fechado'),
        (CLOSED_PRIVATE, 'Fechado (Privado)'),
        (REQUEST, 'Pedido'),
        (REQUEST_PRIVATE, 'Pedido (Privado)'),
        (OPEN, 'Aberta'),
    )

    non_member_permission = IntegerField(choices=NON_MEMBER_PERMISSION_CHOICES, default=SECRET)

    def __str__(self):
        return self.name


class GroupMember(Model):
    group = ForeignKey(Group, on_delete=models.CASCADE, related_name='member_roles')
    member = ForeignKey(User, on_delete=models.CASCADE, related_name='group_roles')
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
