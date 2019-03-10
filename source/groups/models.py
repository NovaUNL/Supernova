from django.db import models as djm

from college.models import Place
from users.models import User


def group_profile_pic_path(group, filename):
    return f'g/{group.id}/pic.{filename.split(".")[-1]}'


class Role(djm.Model):
    name = djm.CharField(max_length=32)
    is_group_admin = djm.BooleanField(default=False)
    is_group_manager = djm.BooleanField(default=False)


class Group(djm.Model):
    abbreviation = djm.CharField(max_length=64, null=True, blank=True)
    name = djm.CharField(max_length=65)
    description = djm.TextField()
    members = djm.ManyToManyField(User, through='GroupMember')
    roles = djm.ManyToManyField(Role, through='GroupRole')
    place = djm.ForeignKey(Place, on_delete=djm.SET_NULL, null=True, blank=True)
    image = djm.ImageField(upload_to=group_profile_pic_path, null=True, blank=True)

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

    type = djm.IntegerField(choices=GROUP_TYPES)

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

    non_member_permission = djm.IntegerField(choices=NON_MEMBER_PERMISSION_CHOICES, default=SECRET)

    def __str__(self):
        return self.name


class GroupMember(djm.Model):
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE, related_name='member_roles')
    member = djm.ForeignKey(User, on_delete=djm.CASCADE, related_name='group_roles')
    role = djm.ForeignKey(Role, on_delete=djm.PROTECT)


class GroupRole(djm.Model):
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE)
    role = djm.ForeignKey(Role, on_delete=djm.PROTECT)


class Announcement(djm.Model):
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE)
    title = djm.CharField(max_length=256)
    announcement = djm.TextField()
    announcer = djm.ForeignKey(User, on_delete=djm.PROTECT)  # TODO consider user deletion
    datetime = djm.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
