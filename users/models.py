from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, TextField, ForeignKey, DateField, IntegerField, DateTimeField, ManyToManyField, \
    ImageField

from users.utils import user_profile_pic_path


class User(AbstractUser):
    nickname = TextField(null=True, max_length=20, verbose_name='Alcunha')
    birth_date = DateField(null=True, verbose_name='Nascimento')
    last_activity = DateTimeField()
    residence = TextField(max_length=50, null=True, blank=True, verbose_name='Residência')
    picture = ImageField(upload_to=user_profile_pic_path, null=True, blank=True, verbose_name='Foto')
    webpage = TextField(max_length=200, null=True, blank=True, verbose_name='Página pessoal')

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
    profile_visibility = IntegerField(choices=PROFILE_VISIBILITY_CHOICES, default=0)

    MALE = 0
    FEMALE = 1
    MULTIPLEGENDERS = 2

    GENDER_CHOICES = (
        (MALE, 'Homem'),
        (FEMALE, 'Mulher'),
        (MULTIPLEGENDERS, 'É complicado')
    )
    gender = IntegerField(choices=GENDER_CHOICES, null=True, blank=True)


class Badge(Model):
    name = TextField(max_length=30, unique=True)
    style = TextField(max_length=15, null=True, default=None)
    users = ManyToManyField(User, through='UserBadge', related_name='badges')


class UserBadge(Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    badge = ForeignKey(Badge, on_delete=models.PROTECT)
    receive_date = DateField(auto_created=True)


class SocialNetworkAccount(Model):
    GITLAB = 0
    GITHUB = 1
    REDDIT = 2
    DISCORD = 3
    LINKEDIN = 4
    TWITTER = 5
    GOOGLEPLUS = 6
    FACEBOOK = 7
    VIMEO = 8
    YOUTUBE = 9
    DEVIANTART = 10
    INSTAGRAM = 11
    FLICKR = 12
    MYANIMELIST = 13
    IMDB = 14

    SOCIAL_NETWORK_CHOICES = (
        (GITLAB, 'GitLab'),
        (GITHUB, 'GitHub'),
        (REDDIT, 'Reddit'),
        (DISCORD, 'Discord'),
        (LINKEDIN, 'Linkedin'),
        (TWITTER, 'Twitter'),
        (GOOGLEPLUS, 'Google+'),
        (FACEBOOK, 'Facebook'),
        (VIMEO, 'Vimeo'),
        (YOUTUBE, 'Youtube'),
        (DEVIANTART, 'DeviantArt'),
        (INSTAGRAM, 'Instagram'),
        (FLICKR, 'Flickr'),
        (MYANIMELIST, 'MyAnimeList'),
        (IMDB, 'IMDB'),
    )
    user = ForeignKey(User, on_delete=models.CASCADE, related_name='social_networks')
    network = IntegerField(choices=SOCIAL_NETWORK_CHOICES)
    profile = TextField(max_length=200)

    def __str__(self):
        return f'{self.SOCIAL_NETWORK_CHOICES[self.network][1]}: {self.profile} ({self.user})'
