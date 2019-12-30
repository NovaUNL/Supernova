from django.db import models as djm
from django.contrib.auth.models import AbstractUser


def user_profile_pic_path(user, filename):
    return f'u/{user.id}/pic.{filename.split(".")[-1]}'


class User(AbstractUser):
    nickname = djm.CharField(null=False, max_length=20, unique=True, verbose_name='Alcunha')
    birth_date = djm.DateField(null=True, verbose_name='Nascimento')
    last_activity = djm.DateTimeField(auto_now_add=True)
    residence = djm.CharField(max_length=64, null=True, blank=True, verbose_name='Residência')
    picture = djm.ImageField(upload_to=user_profile_pic_path, null=True, blank=True, verbose_name='Foto')
    webpage = djm.URLField(null=True, blank=True, verbose_name='Página pessoal')
    primary_student = djm.ForeignKey(
        'college.Student',
        on_delete=djm.PROTECT,
        null=True, blank=True,
        related_name="_user")

    REQUIRED_FIELDS = ['email', 'nickname']

    HIDDEN = 0  # No profile at all
    LIMITED = 1  # Show limited information, only to users
    USERS = 2  # Show full profile, only to users
    MIXED = 3  # Show limited information to visitors, full to users
    PUBLIC = 4  # Show everything to everyone

    PROFILE_VISIBILITY_CHOICES = (
        (HIDDEN, 'Oculto'),
        (LIMITED, 'Limitado'),
        (USERS, 'Utilizadores'),
        (MIXED, 'Misto'),
        (PUBLIC, 'Público'),
    )
    profile_visibility = djm.IntegerField(choices=PROFILE_VISIBILITY_CHOICES, default=0)

    MALE = 0
    FEMALE = 1

    GENDER_CHOICES = (
        (MALE, 'Homem'),
        (FEMALE, 'Mulher')
    )
    gender = djm.IntegerField(choices=GENDER_CHOICES, null=True, blank=True)

    def update_primary(self):
        primary = None
        last_year = 0
        for student in self.students.all():
            if student.last_year is not None and student.last_year > last_year:
                last_year = student.last_year
                primary = student
        if primary is not None:
            self.primary_student = primary
            name = primary.clip_student.name
            if name is not None:
                self.first_name, self.last_name = name.split(' ', 1)


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

    class Meta:
        unique_together = ['user', 'network', 'profile']


class Registration(djm.Model):
    email = djm.EmailField()
    username = djm.CharField(verbose_name='utilizador', max_length=128)
    nickname = djm.CharField(verbose_name='alcunha', max_length=128)
    clip_identifier = djm.CharField(max_length=128)
    password = djm.CharField(verbose_name='palavra-passe', max_length=128)
    creation = djm.DateTimeField(auto_now_add=True)
    token = djm.CharField(max_length=16)
    failed_attempts = djm.IntegerField(default=0)

    def __str__(self):
        return f"{self.username}/{self.nickname}/{self.clip_identifier} -{self.email}"


class VulnerableHash(djm.Model):
    hash = djm.TextField()

    class Meta:
        # TODO figure how to assign to a database
        managed = False
        db_table = 'Hashes'
