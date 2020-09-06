from datetime import datetime

from django.db import models as djm
from django.contrib.auth.models import AbstractUser
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from polymorphic.models import PolymorphicModel


def user_profile_pic_path(user, filename):
    return f'u/{user.id}/pic.{filename.split(".")[-1].lower()}'


class User(AbstractUser):
    nickname = djm.CharField(null=False, max_length=20, unique=True, verbose_name='Alcunha')
    last_nickname_change = djm.DateField(default=datetime(2000, 1, 1).date())
    birth_date = djm.DateField(null=True, blank=True, verbose_name='Nascimento')
    last_activity = djm.DateTimeField(auto_now_add=True)
    residence = djm.CharField(max_length=64, null=True, blank=True, verbose_name='Residência')
    picture = djm.ImageField(upload_to=user_profile_pic_path, null=True, blank=True, verbose_name='Foto')
    webpage = djm.URLField(null=True, blank=True, verbose_name='Página pessoal')

    REQUIRED_FIELDS = ['email', 'nickname']

    NOBODY = 0
    FRIENDS = 1
    USERS = 2
    EVERYBODY = 3
    PROFILE_VISIBILITY_CHOICES = (
        (NOBODY, 'Ninguém'),
        (FRIENDS, 'Amigos'),
        (USERS, 'Utilizadores'),
        (EVERYBODY, 'Todos'))
    profile_visibility = djm.IntegerField(choices=PROFILE_VISIBILITY_CHOICES, default=0)
    info_visibility = djm.IntegerField(choices=PROFILE_VISIBILITY_CHOICES, default=0)
    about_visibility = djm.IntegerField(choices=PROFILE_VISIBILITY_CHOICES, default=0)
    social_visibility = djm.IntegerField(choices=PROFILE_VISIBILITY_CHOICES, default=0)
    groups_visibility = djm.IntegerField(choices=PROFILE_VISIBILITY_CHOICES, default=0)
    enrollments_visibility = djm.IntegerField(choices=PROFILE_VISIBILITY_CHOICES, default=0)
    schedule_visibility = djm.IntegerField(choices=PROFILE_VISIBILITY_CHOICES, default=0)

    MALE = 0
    FEMALE = 1
    OTHER = 2

    GENDER_CHOICES = (
        (MALE, 'Homem'),
        (FEMALE, 'Mulher'),
        (OTHER, 'Outro')
    )
    gender = djm.IntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    about = MarkdownxField(blank=True, null=True)
    # Cached fields
    is_student = djm.BooleanField(default=False)
    is_teacher = djm.BooleanField(default=False)

    @property
    def about_html(self):
        return markdownify(self.about)

    def updated_cached(self):
        changed = False
        is_student = self.students.exists()
        if self.is_student != is_student:
            self.is_student = is_student
            changed = True
        is_teacher = self.teachers.exists()
        if self.is_teacher != is_teacher:
            self.is_teacher = is_teacher
            changed = True
        if changed:
            self.save()

    class Meta:
        permissions = [('full_student_access', 'Can browse the system as if it was the university one')]


class Badge(djm.Model):
    name = djm.CharField(max_length=32, unique=True)
    style = djm.CharField(max_length=15, null=True, default=None)
    users = djm.ManyToManyField(User, through='UserBadge', related_name='badges')


class UserBadge(djm.Model):
    user = djm.ForeignKey(User, on_delete=djm.CASCADE)
    badge = djm.ForeignKey(Badge, on_delete=djm.PROTECT)
    receive_date = djm.DateField(auto_created=True)


class SocialNetworkAccount(djm.Model):
    GITLAB = 0
    GITHUB = 1
    LINKEDIN = 2
    MASTODON = 3
    VIMEO = 4
    YOUTUBE = 5
    DEVIANTART = 6
    FLICKR = 7
    THINGIVERSE = 8
    WIKIPEDIA = 9

    SOCIAL_NETWORK_CHOICES = (
        (GITLAB, 'GitLab'),
        (GITHUB, 'GitHub'),
        (LINKEDIN, 'Linkedin'),
        (MASTODON, 'Mastodon'),
        (VIMEO, 'Vimeo'),
        (YOUTUBE, 'Youtube'),
        (DEVIANTART, 'DeviantArt'),
        (FLICKR, 'Flickr'),
        (THINGIVERSE, 'Thingiverse'),
        (WIKIPEDIA, 'Wikipedia'),
    )

    user = djm.ForeignKey(User, on_delete=djm.CASCADE, related_name='social_networks')
    network = djm.IntegerField(choices=SOCIAL_NETWORK_CHOICES)
    profile = djm.CharField(max_length=128)

    def __str__(self):
        return f'{self.SOCIAL_NETWORK_CHOICES[self.network][1]}: {self.profile} ({self.user})'

    def network_str(self):
        return self.SOCIAL_NETWORK_CHOICES[self.network][1]

    class Meta:
        unique_together = ['user', 'network', 'profile']


class Registration(djm.Model):
    email = djm.EmailField()
    username = djm.CharField(verbose_name='utilizador', max_length=128)
    nickname = djm.CharField(verbose_name='alcunha', max_length=128)
    student = djm.CharField(max_length=128)
    password = djm.CharField(verbose_name='palavra-passe', max_length=128)
    creation = djm.DateTimeField(auto_now_add=True)
    token = djm.CharField(max_length=16)
    failed_attempts = djm.IntegerField(default=0)

    def __str__(self):
        return f"{self.username}/{self.nickname}/{self.student} -{self.email}"


class VulnerableHash(djm.Model):
    hash = djm.TextField()

    class Meta:
        # TODO figure how to assign to a database
        managed = False
        db_table = 'Hashes'


class Invite(djm.Model):
    """A invite issued by an used to allow other :py:class:`User` to register"""
    #: The :py:class:`User` that issued the invite
    issuer = djm.ForeignKey(User, on_delete=djm.PROTECT, related_name='invites')
    #: The token that is used to activate the invite
    token = djm.CharField(max_length=16, unique=True)
    #: Date on which the invite was created
    created = djm.DateTimeField(auto_now_add=True)
    #: Date after which the invite is no longer valid
    expiration = djm.DateTimeField()
    #: :py:class:`Registration` that used the invite
    # FIXME Invite rendered useless if another registration conflicts with this one before it is confirmed.
    registration = djm.ForeignKey(Registration, null=True, blank=True, on_delete=djm.SET_NULL, related_name='invites')
    #: :py:class:`User` that resulted from the usage of this invite
    resulting_user = djm.OneToOneField(User, null=True, blank=True, on_delete=djm.SET_NULL)
    #: Whether the invite got revoked
    revoked = djm.BooleanField(default=False)

    def __str__(self):
        return f"{self.issuer.nickname}:{self.token}"


class Subscriptible(djm.Model):
    """
    | A data type which can be subscribed to
    | (Meant to be inherited)
    """
    #: The id field, but renamed to avoid collisions upon multiple inheritance
    subscriptible_id = djm.AutoField(primary_key=True)
    #: :py:class:`users.models.User` that subscribe to this object.
    subscribers = djm.ManyToManyField(User, through='Subscription', related_name='subscriptibles')


class Subscription(PolymorphicModel):
    """
    A notification points to unknown past actions with a particular relevance.
    """
    #: :py:class:`Subscribable` that this subscription targets
    to = djm.ForeignKey(Subscriptible, on_delete=djm.CASCADE, related_name='subscriptions')
    #: :py:class:`users.models.User` that wishes to be notified.
    subscriber = djm.ForeignKey(User, on_delete=djm.CASCADE, related_name='subscriptions')
    #: Datetime at which the activity happened
    issue_timestamp = djm.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.issue_timestamp}({self.destinatary})'


class Activity(PolymorphicModel):
    """
    An activity is an action taken by a user at a given point in time.
    """
    #: :py:class:`User` that made this activity.
    user = djm.ForeignKey(User, on_delete=djm.CASCADE, related_name='activities')
    #: The id field, but renamed to avoid collisions upon multiple inheritance
    activity_id = djm.AutoField(primary_key=True)
    #: Datetime at which the activity happened
    timestamp = djm.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.datetime}({self.user})'

    class Meta:
        verbose_name_plural = "activities"


class Notification(PolymorphicModel):
    """
    A notification points to unknown past actions with a particular relevance.
    """
    #: :py:class:`users.models.User` that received the notification.
    recipient = djm.ForeignKey(User, on_delete=djm.CASCADE, related_name='notifications')
    #: Datetime at which the notification was issued
    issue_timestamp = djm.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.issue_timestamp}({self.destinatary})'
