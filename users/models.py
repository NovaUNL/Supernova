from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, TextField, ForeignKey, DateField


class User(AbstractUser):
    nickname = TextField(null=True, max_length=20)
    birth_date = DateField(null=True)

class Badge(Model):
    name = TextField(max_length=30, unique=True, default=None)


class UserBadge(Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    badge = ForeignKey(Badge, on_delete=models.PROTECT)

