from django.db import models
from django.db.models import Model, IntegerField, TextField, ForeignKey, DateField, BooleanField, OneToOneField, \
    TimeField

from kleep.models import KLEEP_TABLE_PREFIX
from college.models import Building
from store.models import Sellable


class Service(Model):
    name = TextField(max_length=50)
    building = ForeignKey(Building, null=True, blank=True, on_delete=models.SET_NULL)
    map_tag = TextField(max_length=15)
    opening = TimeField(null=True, blank=True)
    lunch_start = TimeField(null=True, blank=True)  # For a bar this is the meal time, for other places this is a break
    lunch_end = TimeField(null=True, blank=True)
    closing = TimeField(null=True, blank=True)
    open_saturday = BooleanField(default=False)
    open_sunday = BooleanField(default=False)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'services'

    def __str__(self):
        return "{} ({})".format(self.name, self.building)


class Bar(Model):
    service = OneToOneField(Service, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'bars'

    def __str__(self):
        return str(self.service)


class BarDailyMenu(Sellable, Model):
    bar = ForeignKey(Bar, on_delete=models.CASCADE)
    date = DateField(auto_now_add=True)
    item = TextField(max_length=100)
    price = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'bar_daily_menus'

    def __str__(self):
        return f'{self.item}, {self.bar} ({self.date})'


class BarPrice(Sellable, Model):
    bar = ForeignKey(Bar, on_delete=models.CASCADE)
    item = TextField(max_length=100)
    price = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'bar_prices'

    def __str__(self):
        return '%s, %0.2f€ (%s)' % (self.item, self.price / 100, self.bar.service.name)
