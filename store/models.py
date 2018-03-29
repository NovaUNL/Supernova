from django.db import models
from django.db.models import Model, IntegerField, TextField, ForeignKey

from kleep.models import KLEEP_TABLE_PREFIX, Profile, Group, Sellable


class StoreItem(Sellable, Model):
    name = TextField(max_length=100)
    description = TextField()
    price = IntegerField()
    stock = IntegerField(default=-1)
    seller = ForeignKey(Group, on_delete=models.CASCADE)
    img_url = TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'store_items'

    def __str__(self):
        return '%s (%d.%02d€)' % (self.name, int(self.price / 100), self.price % 100)


class ClassifiedItem(Sellable, Model):
    name = TextField(max_length=100)
    description = TextField()
    price = IntegerField()
    seller = ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'classified_items'

    def __str__(self):
        return self.name
