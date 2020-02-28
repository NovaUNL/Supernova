from django.db import models as djm
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from college.choice_types import WEEKDAY_CHOICES
from college.models import Place
from users.models import User


def group_profile_pic_path(group, filename):
    return f'g/{group.id}/pic.{filename.split(".")[-1]}'


class Group(djm.Model):
    """
    | A set of :py:class:`users.models.User` who represent a collective entity, such as an institutional division,
      students nuclei, working group, ...
    | Groups are meant to be self-administered with each user having one :py:class:`Role`,
    """
    #: A short texual identifier.
    abbreviation = djm.CharField(max_length=64, null=True, blank=True)
    #: The group's full name.
    name = djm.CharField(max_length=65)
    #: A description that defines the group.
    description = MarkdownxField(blank=True, null=True)
    #: The members that are part of this group (belong to it).
    members = djm.ManyToManyField(User, through='Membership', related_name='memberships')
    #: The subscribers of this group (do not necessarily belong to it).
    subscribers = djm.ManyToManyField(User, blank=True, related_name='group_subscriptions')
    #: The place where this group is headquartered and commonly found.
    place = djm.ForeignKey(Place, on_delete=djm.SET_NULL, null=True, blank=True)
    #: An image that presents this group.
    image = djm.ImageField(upload_to=group_profile_pic_path, null=True, blank=True)

    #: The default role that users get assigned upon joining this group.
    default_role = djm.ForeignKey('Role', null=True, blank=True, on_delete=djm.SET_NULL, related_name='default_to')

    INSTITUTIONAL = 0
    NUCLEI = 1
    ACADEMIC_ASSOCIATION = 2
    PEDAGOGIC = 3
    PRAXIS = 4
    COMMUNITY = 5

    GROUP_TYPES = (
        (INSTITUTIONAL, 'Intitucional'),
        (NUCLEI, 'Núcleo'),
        (ACADEMIC_ASSOCIATION, 'Associação'),
        (PEDAGOGIC, 'Pedagógico'),
        (PRAXIS, 'CoPe'),
        (COMMUNITY, 'Comunidade'),
    )
    GROUP_CODES = ['inst', 'nucl', 'inst', 'ped', '_', 'com']

    type = djm.IntegerField(choices=GROUP_TYPES)

    #: | Flag for :py:attr:`outsiders_openness`
    #: | Group unlisted and and closed to new members.
    SECRET = 0
    #: | Flag for :py:attr:`outsiders_openness`
    #: | Group is listed and visible but outsiders cannot apply for membership.
    CLOSED = 1
    #: | Flag for :py:attr:`outsiders_openness`
    #: | Group allows outsiders to apply for membership
    REQUEST = 2
    #: | Flag for :py:attr:`outsiders_openness`
    #: | Group allows outsiders to join, with :py:attr:`default_role`
    OPEN = 3

    OPENNESS_CHOICES = (
        (SECRET, 'Secreto'),
        (CLOSED, 'Fechado'),
        (REQUEST, 'Pedido'),
        (OPEN, 'Aberta'),
    )

    #: | Numeric flag that toggles the visibility and entrance acceptability of this group
    outsiders_openness = djm.IntegerField(choices=OPENNESS_CHOICES, default=SECRET)

    def __str__(self):
        return self.name

    @property
    def description_html(self):
        return markdownify(self.description)

class Role(djm.Model):
    """
    | A role is both a title for users within a group and a set of permissions within that same group.
    """
    #: Role textual name.
    name = djm.CharField(max_length=128)
    #: :py:class:`Group` this role belongs to.
    group = djm.ForeignKey('Group', on_delete=djm.CASCADE, related_name='roles')
    #: God mode, permission to to anything within this group.
    is_admin = djm.BooleanField(default=False)
    #: Permission to modify aspects of the group roles.
    can_modify_roles = djm.BooleanField(default=False)
    #: Permission to assign roles to other users.
    can_assign_roles = djm.BooleanField(default=False)
    #: Permission to announce as group vocals.
    can_announce = djm.BooleanField(default=False)
    #: Permission to read conversations from outsiders to this group.
    can_read_conversations = djm.BooleanField(default=False)
    #: Permission to write in conversations from outsiders to this group.
    can_write_conversations = djm.BooleanField(default=False)
    #: Permission to read internal private conversations of this group.
    can_read_internal_conversations = djm.BooleanField(default=False)
    #: Permission to write in internal private conversations of this group.
    can_write_internal_conversations = djm.BooleanField(default=False)
    #: Permission to read the documents that are private to this group.
    can_read_internal_documents = djm.BooleanField(default=False)
    #: Permission to write the documents that are private to this group.
    can_write_internal_documents = djm.BooleanField(default=False)
    #: Permission to write the documents that this group presents to the public.
    can_write_public_documents = djm.BooleanField(default=False)
    #: Permission to change the group schedule.
    can_change_schedule = djm.BooleanField(default=False)

    def __str__(self):
        return self.name


class Membership(djm.Model):
    """ Membership M2M table ( :py:class:`Group` >--< :py:class:`users.models.User` )"""
    #: :py:class:`Group` referred to by this membership
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE, related_name='member_roles')
    #: :py:class:`users.models.User` referred to by this membership
    member = djm.ForeignKey(User, on_delete=djm.CASCADE, related_name='group_roles')
    #: :py:class:`Role` conferred
    role = djm.ForeignKey(Role, on_delete=djm.PROTECT)

    def __str__(self):
        return f'{self.member.nickname} -> {self.role} -> {self.group}'


class Activity(djm.Model):
    """
    | An activity is an action taken by a group at a given point in time. These end up building an activity log which
      is meant to be used as a feed
    """
    #: :py:class:`Group` that had this activity
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE)
    #: :py:class:`users.models.User` that triggered the activity.
    author = djm.ForeignKey(User, on_delete=djm.PROTECT)
    #: Datetime at which the trigger happened
    datetime = djm.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.datetime}({self.author})'


class Announcement(Activity):
    """The activity that represents the publishing of a textual information by a :py:class:`Group`"""
    #: Announcement title.
    title = djm.CharField(max_length=256)
    #: Announcement markdown.
    content = MarkdownxField()

    def __str__(self):
        return self.title


class ScheduleEntry(djm.Model):
    """Base entry in this :py:class:`Group` 's activity schedule."""
    #: :py:class:`Group` with this entry
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE)
    #: (Optional) Title for the entry
    title = djm.CharField(max_length=128, blank=True, null=True)
    #: Whether the entry occurrence scheduling is cancelled
    revoked = djm.BooleanField(default=False)


class ScheduleOnce(ScheduleEntry):
    """Represents a one-time entry in this :py:class:`Group` 's activity schedule."""
    #: The date at which this event is set to happen
    datetime = djm.DateTimeField()
    #: The predicted duration of this event interval
    duration = djm.IntegerField()


class SchedulePeriodic(ScheduleEntry):
    """Represents a periodic entry in this group's activity schedule. This entry happens weekly."""
    #: The weekday on which this event is set to happen
    weekday = djm.IntegerField(choices=WEEKDAY_CHOICES)
    #: The predicted duration of these recurring events
    duration = djm.IntegerField()
    #: The date on which this scheduling was defined to start
    start_date = djm.DateField(auto_now_add=True)
    #: The date on which this scheduling lost its validity
    end_date = djm.DateField(blank=True, null=True, default=None)


class ScheduleRevoke(Activity):
    """ An activity log entry to signal that a :py:class:`ScheduleEntry` has been permanently revoked."""
    #: (Optional) Description for this schedule update
    description = djm.CharField(max_length=256, blank=True, null=True)
    #: The :py:class:`ScheduleEntry` that this update refers to
    entry = djm.ForeignKey(ScheduleEntry, on_delete=djm.CASCADE, related_name='revocation')
    #: The :py:class:`ScheduleEntry` that replaces the revoked entry
    replacement = djm.ForeignKey(
        ScheduleEntry,
        on_delete=djm.SET_NULL,
        blank=True,
        null=True,
        related_name='replaced_revoked_entries')


class ScheduleSuspension(Activity):
    """An activity log entry to signal that a :py:class:`SchedulePeriodic` has been temporarily postponed."""
    #: The :py:class:`SchedulePeriodic` that this exception refers to
    entry = djm.ForeignKey(SchedulePeriodic, on_delete=djm.CASCADE, related_name='suspensions')
    #: An optional description (such as the cause of this exception).
    description = djm.TextField(blank=True, null=True)
    #: The initial date on which the suspension starts
    start_date = djm.DateField(auto_now_add=True)
    #: The date on which the suspension ends
    end_date = djm.DateField(blank=True, null=True, default=None)
    #: A :py:class:`ScheduleEntry` that temporarily replaces the suspended entry
    replacement = djm.ForeignKey(
        ScheduleEntry,
        on_delete=djm.SET_NULL,
        blank=True,
        null=True,
        related_name='replaced_suspended_entries')


class Gallery(djm.Model):
    """A multimedia gallery that belongs to a :py:class:`Group`"""
    #: Gallery title
    title = djm.CharField(max_length=256)
    #: Owner :py:class:`Group`
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE)
    #: Gallery absolute position in the group galleries listing
    index = djm.IntegerField(unique=True)


class GalleryItem(djm.Model):
    """A multimedia item in a :py:class:`Gallery`."""
    #: Item :py:class:`Gallery`.
    gallery = djm.ForeignKey(Gallery, on_delete=djm.PROTECT)
    #: An optional caption describing the item
    caption = djm.TextField(blank=True, null=True)
    #: Datetime associated with the item, NOT the datetime at which it has been uploaded
    #: (see :py:class:`GalleryUpload` for upload datetime)
    item_datetime = djm.DateTimeField(auto_now_add=True)
    #: Item absolute position in the gallery
    index = djm.IntegerField(unique=True)


class GalleryUpload(Activity):
    """An activity log entry to signal that a :py:class:`GalleryItem` has been created."""
    #: The item this upload refers to. Nullified if the item gets deleted.
    item = djm.OneToOneField(GalleryItem, blank=True, null=True, on_delete=djm.SET_NULL, related_name="upload")
