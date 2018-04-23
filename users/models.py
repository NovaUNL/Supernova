from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, TextField, ForeignKey, DateField, IntegerField, DateTimeField, ManyToManyField, \
    ImageField


def user_directory_path(instance, filename):
    return f'u/{instance.user.id}/{instance.user}'


class User(AbstractUser):
    nickname = TextField(null=True, max_length=20, verbose_name='Alcunha')
    birth_date = DateField(null=True, verbose_name='Nascimento')
    last_activity = DateTimeField()
    residence = TextField(max_length=50, null=True, blank=True, verbose_name='Residência')
    picture = ImageField(upload_to=user_directory_path, null=True, blank=True, verbose_name='Foto')

    HIDDEN = 1  # No profile at all
    LIMITED = 2  # Show limited information, only to users
    USERS = 3  # Show full profile, only to users
    MIXED = 4  # Show limited information to visitors, full to users
    PUBLIC = 5  # Show everything to everyone

    PROFILE_VISIBILITY_CHOICES = (
        (HIDDEN, 'Oculto'),
        (LIMITED, 'Limitado'),
        (USERS, 'Utilizadores'),
        (MIXED, 'Misto'),
        (PUBLIC, 'Público'),
    )
    profile_visibility = IntegerField(choices=PROFILE_VISIBILITY_CHOICES, default=1)

    MALE = 1
    FEMALE = 2
    MULTIPLEGENDERS = 3

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
    GITLAB = 1
    GITHUB = 2
    REDDIT = 3
    DISCORD = 4
    LINKEDIN = 5
    TWITTER = 6
    GOOGLEPLUS = 7
    FACEBOOK = 8
    VIMEO = 9
    YOUTUBE = 10
    DEVIANTART = 11
    INSTAGRAM = 12
    FLICKR = 13
    MYANIMELIST = 14
    IMDB = 15

    SOCIAL_NETWORK_CHOICES = (
        (GITLAB, 'GitLab'),
        (GITHUB, 'GitHub'),
        (REDDIT, 'Reddit'),
        (DISCORD, 'Discord'),
        (LINKEDIN, 'Linkedin'),
        (GOOGLEPLUS, 'Google+'),
        (FACEBOOK, 'Facebook'),
        (VIMEO, 'Vimeo'),
        (YOUTUBE, 'Youtube'),
        (DEVIANTART, 'DeviantArt'),
        (INSTAGRAM, 'Instagram'),
        (FLICKR, 'Flickr'),
        (MYANIMELIST, 'MyAnimeList'),
        (MYANIMELIST, 'IMDB'),
    )
    user = ForeignKey(User, on_delete=models.CASCADE)
    network = IntegerField(choices=SOCIAL_NETWORK_CHOICES)
    profile = TextField(max_length=200)
