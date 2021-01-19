from datetime import datetime, time

import reversion
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models as djm, transaction
from django.urls import reverse
from imagekit.models import ImageSpecField
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from pilkit.processors import ResizeToFit
from polymorphic.models import PolymorphicModel

from college.choice_types import WEEKDAY_CHOICES
from users import models as users


def group_icon_path(group, filename):
    return f'g/{group.id}/icon.{filename.split(".")[-1].lower()}'


def group_image_path(group, filename):
    return f'g/{group.id}/image.{filename.split(".")[-1].lower()}'


@reversion.register()
class Group(djm.Model):
    """
    | A set of :py:class:`users.models.User` who represent a collective entity, such as an institutional division,
      students nuclei, working group, ...
    | Groups are meant to be self-administered with each user having one :py:class:`Role`,
    """
    #: A short textual descriptor. Used as a group identifier.
    abbreviation = djm.CharField(max_length=64, unique=True, db_index=True)
    #: The group's full name.
    name = djm.CharField(max_length=65)
    #: A description that defines the group.
    description = MarkdownxField(blank=True, null=True)
    #: | The members that are part of this group (belong to it).
    #: | The related_name _ prefix is due to the Django own groups
    #: | TODO either integrate or remove django groups
    members = djm.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', related_name='groups_custom')
    #: The place where this group is headquartered and commonly found.
    place = djm.ForeignKey('college.Place', on_delete=djm.SET_NULL, null=True, blank=True, related_name='groups')
    #: This group's icon
    icon = djm.ImageField(upload_to=group_icon_path, null=True, blank=True)
    #: An image that illustrates this group
    image = djm.ImageField(upload_to=group_image_path, null=True, blank=True)
    icon_small = ImageSpecField(
        source='icon',
        processors=[ResizeToFit(*settings.SMALL_ICON_SIZE)],
        format='PNG')
    icon_big = ImageSpecField(
        source='icon',
        processors=[ResizeToFit(*settings.BIG_ICON_SIZE)],
        format='PNG')
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFit(*settings.THUMBNAIL_SIZE)],
        format='JPEG',
        options={'quality': settings.MEDIUM_QUALITY})

    subscriptions = GenericRelation(
        users.Subscription,
        content_type_field='to_content_type',
        object_id_field='to_object_id',
        related_query_name='group')

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
    #: | Whether the group really is the group
    official = djm.BooleanField(default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('groups:group', args=[self.abbreviation])

    @property
    def description_html(self):
        return markdownify(self.description)

    def notify_subscribers(self, activity):
        for subscription in self.subscriptions.all():
            # TODO bulk insert
            GroupActivityNotification.objects.create(activity=activity, receiver=subscription.subscriber)
            subscription.subscriber.clear_notification_cache()

    @property
    def thumbnail_or_default(self):
        if self.image:
            return self.image_thumbnail.url


@reversion.register()
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
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE, related_name='memberships')
    #: :py:class:`users.models.User` referred to by this membership
    member = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.CASCADE, related_name='memberships')
    #: :py:class:`Role` conferred
    role = djm.ForeignKey(Role, on_delete=djm.PROTECT, related_name='memberships')
    #: Membership start
    since = djm.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['group', 'member']]

    def __str__(self):
        return f'{self.member.nickname} -> {self.role} -> {self.group}'


class MembershipRequest(djm.Model):
    """Requests to obtain :py:class:`Membership` in a :py:class:`Group`"""
    #: Requesting :py:class:`users.models.User`
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.CASCADE, related_name='membership_requests')
    #: Requested :py:class:`Group`
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE, related_name='membership_requests')
    #: Datetime when the trigger happened
    datetime = djm.DateTimeField(auto_now_add=True)
    #: Whether the request was granted and the user gained a membership
    granted = djm.BooleanField(default=None, null=True, blank=True)
    #: Some message that was left with the request
    message = djm.TextField(default=None, blank=True, null=True, max_length=1000)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f'{self.user.nickname} membership request to {self.group}'

    def accept(self):
        with transaction.atomic():
            self.granted = True
            self.save(update_fields=['granted'])
            Membership.objects.create(group=self.group, member=self.user, role=self.group.default_role)

    def deny(self):
        self.granted = False
        self.save(update_fields=['granted'])


class Activity(PolymorphicModel):
    """
    | An activity is an action taken by a group at a given point in time. These end up building an activity log which
      is meant to be used as a feed
    """
    #: :py:class:`Group` that had this activity
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE, related_name='activities')
    #: :py:class:`users.models.User` that triggered the activity.
    author = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.PROTECT, related_name='group_activity')
    #: Datetime when the trigger happened
    datetime = djm.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.datetime}({self.author})'

    @property
    def activity_name(self):
        return None

    class Meta:
        verbose_name_plural = "activities"


@reversion.register()
class Announcement(Activity):
    """The activity that represents the publishing of a textual information by a :py:class:`Group`"""
    #: Announcement title.
    title = djm.CharField(max_length=256)
    #: Announcement markdown.
    content = MarkdownxField()

    def __str__(self):
        return f"{self.title}"

    @property
    def content_html(self):
        return markdownify(self.content)

    @property
    def activity_name(self):
        return 'Anúncio'

    @property
    def link_to(self):
        return reverse('groups:announcement', args=[self.group.abbreviation, self.id])


class ScheduleEntry(PolymorphicModel):
    """Base entry in this :py:class:`Group` 's activity schedule."""
    #: :py:class:`Group` with this entry
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE, related_name='schedule_entries')
    #: (Optional) Title for the entry
    title = djm.CharField(max_length=128, blank=True, null=True)
    #: Whether the entry occurrence scheduling is cancelled
    revoked = djm.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'schedule entries'


class ScheduleOnce(ScheduleEntry):
    """Represents a one-time entry in this :py:class:`Group` 's activity schedule."""
    #: The date at which this event is set to happen
    datetime = djm.DateTimeField()
    #: The predicted duration of this event interval
    duration = djm.IntegerField()

    def __str__(self):
        return f"{self.title}, dia {datetime.strftime(self.datetime, '%d/%m/%Y %H:%M')}"


class SchedulePeriodic(ScheduleEntry):
    """Represents a periodic entry in this group's activity schedule. This entry happens weekly."""
    #: The weekday on which this event is set to happen
    weekday = djm.IntegerField(choices=WEEKDAY_CHOICES)
    #: The time at which the event occurs.
    time = djm.TimeField()
    #: The predicted duration of these recurring timeline
    duration = djm.IntegerField()
    #: The date on which this scheduling was defined to start
    start_date = djm.DateField()
    #: The date on which this scheduling lost its validity
    end_date = djm.DateField(blank=True, null=True, default=None)

    def __str__(self):
        return f"{self.title}, {self.get_weekday_display()} ás {time.strftime(self.time, '%H:%M')}"


class ScheduleCreation(Activity):
    """An activity log entry to signal that a :py:class:`ScheduleEntry` has been created."""
    #: The :py:class:`ScheduleEntry` that this creation refers to
    entry = djm.OneToOneField(ScheduleEntry, on_delete=djm.CASCADE, related_name='creation')

    def __str__(self):
        return f"@{self.group.abbreviation}: {self.entry}"

    @property
    def title(self):
        return str(self.entry)

    @property
    def activity_name(self):
        return 'Agendamento'

    @property
    def link_to(self):
        return None


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

    def __str__(self):
        if self.replacement is None:
            return f"Suspensas as actividades de {self.entry} entre {self.start_date} e {self.end_date}"
        else:
            return f"Alterações nas actividades de {self.entry.title} entre {self.start_date} e {self.end_date}."

    @property
    def activity_name(self):
        return 'Alteração agenda'

    @property
    def link_to(self):
        return reverse('groups:calendar_manage', args=[self.entry.group.abbreviation])


class ScheduleRevoke(Activity):
    """ An activity log entry to signal that a :py:class:`ScheduleEntry` has been permanently revoked."""
    #: (Optional) Description for this schedule update
    description = djm.CharField(max_length=256, blank=True, null=True)
    #: The :py:class:`ScheduleEntry` that this update refers to
    entry = djm.OneToOneField(ScheduleEntry, on_delete=djm.CASCADE, related_name='revocation')
    #: The :py:class:`ScheduleEntry` that replaces the revoked entry
    replacement = djm.ForeignKey(
        ScheduleEntry,
        on_delete=djm.SET_NULL,
        blank=True,
        null=True,
        related_name='replaced_revoked_entries')

    def __str__(self):
        return f"Cancelamento de {self.entry}"

    @property
    def activity_name(self):
        return 'Cancelamento'

    @property
    def link_to(self):
        return reverse('groups:calendar_manage', args=[self.entry.group.abbreviation])


class Event(djm.Model):
    """
    While a ScheduleEntry represents a casual event, part of the regular routine, mostly focused towards group members
    which are assumed to attend by default; an Event is assumed as something that stands off, to which many users do
    not want to attend, can have an associated cost and tends to be open towards outsiders.
    """
    #: :py:class:`Group` that will have this event
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE, related_name='events')
    #: A short title that identifies the event
    title = djm.CharField(max_length=200)
    #: A textual description of the event
    description = MarkdownxField()
    #: Date on which the event happens
    start_date = djm.DateField()
    #: Expected duration for the event
    duration = djm.IntegerField(null=True, blank=True)
    #: Location where the event happens
    place = djm.ForeignKey('college.Place', null=True, blank=True, on_delete=djm.SET_NULL, related_name='events')
    #: Limit of persons in this event
    capacity = djm.IntegerField(null=True, blank=True)
    #: | Flag telling that this is the official enrollment platform for the event
    #: | This essentially means that constraints must be enforced.
    enroll_here = djm.BooleanField(default=True)
    #: Cost in cents
    cost = djm.IntegerField()

    #: An event that does not fit into any other category
    GENERIC = 0
    #: An event where people talk about something to an audience
    TALK = 1
    #: An event where something is taught to its attendees
    WORKSHOP = 2
    #: An event which where attendees celebrate
    PARTY = 3
    #: An event where a competition takes place
    CONTEST = 4
    #: An event where an exposition takes place
    FAIR = 5
    #: An event which serves to aggregate people with a certain background
    MEETING = 6
    #: Enumeration with the possible types of event
    CHOICES = (
        (GENERIC, 'Genérico'),
        (TALK, 'Palestra'),
        (WORKSHOP, 'Workshop'),
        (PARTY, 'Festa'),
        (CONTEST, 'Concurso'),
        (FAIR, 'Feira'),
        (MEETING, 'Encontro'),
    )

    #: The type of this event (enumeration)
    type = djm.IntegerField(choices=CHOICES)
    #: Users who are going to this event (and are confirmed)
    attendees = djm.ManyToManyField(settings.AUTH_USER_MODEL, related_name='attended_events')
    #: Users who desire to go to this event and await for approval or vacancies
    queued = djm.ManyToManyField(settings.AUTH_USER_MODEL, related_name='queued_events', through='EventUserQueue')
    #: Users who want to receive information about changes to this event
    subscribers = djm.ManyToManyField(settings.AUTH_USER_MODEL, related_name='event_subscription')

    def __str__(self):
        return f"{self.title}"


class EventAnnouncement(Activity):
    """An activity log to signal event announcements."""
    #: The event being announced
    event = djm.OneToOneField(Event, on_delete=djm.CASCADE)

    def __str__(self):
        return str(self.event)

    @property
    def activity_name(self):
        return 'Anúncio'

    @property
    def link_to(self):
        # FIXME point to a more specific page once said page exists
        return reverse('groups:group', args=[self.event.group.abbreviation])


class EventUserQueue(djm.Model):
    """A queue of users desiring to attend an event"""
    #: Event being queued for
    event = djm.ForeignKey(Event, on_delete=djm.CASCADE, related_name='queue_positions')
    #: Queued user
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.CASCADE, related_name='event_queue_positions')
    #: Time at which the user entered the queue
    timestamp = djm.DateTimeField(auto_now_add=True)
    #: Flag that signals users as missing the event fee payment
    awaiting_payment = djm.BooleanField(default=True)


class Gallery(djm.Model):
    """A multimedia gallery that belongs to a :py:class:`Group`"""
    #: Gallery title
    title = djm.CharField(max_length=256)
    #: Owner :py:class:`Group`
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE, related_name='galleries')
    #: Gallery absolute position in the group galleries listing
    index = djm.IntegerField(unique=True)


class GalleryItem(djm.Model):
    """A multimedia item in a :py:class:`Gallery`."""
    #: Item :py:class:`Gallery`.
    gallery = djm.ForeignKey(Gallery, on_delete=djm.PROTECT, related_name='items')
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


class GroupActivityNotification(users.Notification):
    """A notification of group activity, meant to be received by subscribers."""
    activity = djm.ForeignKey(Activity, on_delete=djm.CASCADE)

    def to_api(self):
        result = super(GroupActivityNotification, self).to_api()
        result['message'] = str(self.activity)
        result['url'] = self.activity.link_to
        result['type'] = self.activity.activity_name
        result['entity'] = f'@{self.activity.group.abbreviation}'
        return result

    def to_url(self):
        return self.activity.link_to

    def __str__(self):
        return str(self.activity)
