from django.db import models
from django.db.models import Model, IntegerField, TextField, ForeignKey

from groups.models import Group
from users.models import User


class Sellable:
    price = IntegerField()

    def price_str(self):
        return '%0.2f' % (self.price / 100)


class Item(Sellable, Model):
    name = TextField(max_length=100)
    description = TextField()
    price = IntegerField()
    stock = IntegerField(default=-1)
    seller = ForeignKey(Group, on_delete=models.CASCADE)
    img_url = TextField(null=True, blank=True)

    class Meta:
        unique_together = ['name', 'seller']

    def __str__(self):
        return '%s (%d.%02d€)' % (self.name, int(self.price / 100), self.price % 100)


class ClassifiedItem(Sellable, Model):
    name = TextField(max_length=100)
    description = TextField()
    price = IntegerField()
    seller = ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name', 'seller']

    def __str__(self):
        return self.name
