from django.db import models as djm

from groups.models import Group
from users.models import User


class Sellable:
    price = djm.IntegerField()

    def price_str(self):
        return '%0.2f' % (self.price / 100)


class Item(Sellable, djm.Model):
    name = djm.CharField(max_length=128)
    description = djm.TextField()
    price = djm.IntegerField()
    stock = djm.IntegerField(default=-1)
    seller = djm.ForeignKey(Group, on_delete=djm.CASCADE)
    img_url = djm.TextField(null=True, blank=True)

    class Meta:
        unique_together = ['name', 'seller']

    def __str__(self):
        return '%s (%d.%02d€)' % (self.name, int(self.price / 100), self.price % 100)


class ClassifiedItem(Sellable, djm.Model):
    name = djm.CharField(max_length=128)
    description = djm.TextField()
    price = djm.IntegerField()
    seller = djm.ForeignKey(User, on_delete=djm.CASCADE)

    class Meta:
        unique_together = ['name', 'seller']

    def __str__(self):
        return self.name
