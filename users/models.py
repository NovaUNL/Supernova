from django.db import models
from django.contrib.auth.models import User
from django.db.models import Model, TextField, ForeignKey, DateField, OneToOneField


class Profile(Model):
    name = TextField()
    nickname = TextField()
    birth_date = DateField()
    user = OneToOneField(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "{} ({})".format(self.nickname, self.name)


class Badge(Model):
    name = TextField(max_length=30, unique=True, default=None)


class UserBadge(Model):
    user = ForeignKey(Profile, on_delete=models.CASCADE)
    badge = ForeignKey(Badge, on_delete=models.PROTECT)