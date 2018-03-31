from django.db import models
from django.contrib.auth.models import User
from django.db.models import Model, TextField, ForeignKey, DateField, OneToOneField

KLEEP_TABLE_PREFIX = 'kleep_'


class Profile(Model):
    name = TextField()
    nickname = TextField()
    birth_date = DateField()
    user = OneToOneField(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'users'

    def __str__(self):
        return "{} ({})".format(self.nickname, self.name)


class Badge(Model):
    name = TextField(max_length=30, unique=True, default=None)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'badges'


class UserBadges(Model):
    user = ForeignKey(Profile, on_delete=models.CASCADE)
    badge = ForeignKey(Badge, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'user_badges'
