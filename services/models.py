from django.db import models
from django.db.models import Model, IntegerField, TextField, ForeignKey, DateField, BooleanField, TimeField

from college.models import Building, Place
from store.models import Sellable


class Service(Model):
    name = TextField(max_length=50)
    place = ForeignKey(Place, null=True, blank=True, on_delete=models.SET_NULL)
    map_tag = TextField(max_length=15)
    opening = TimeField(null=True, blank=True)
    restaurant = BooleanField()
    lunch_start = TimeField(null=True, blank=True)  # For a bar this is the meal time, for other places this is a break
    lunch_end = TimeField(null=True, blank=True)
    closing = TimeField(null=True, blank=True)
    open_saturday = BooleanField(default=False)
    open_sunday = BooleanField(default=False)

    class Meta:
        unique_together = ['name', 'place']
        ordering = ['name']

    def __str__(self):
        return "{} ({})".format(self.name, self.place.building)


class Dish(Model):
    name = TextField(max_length=100)
    price = IntegerField()

    class Meta:
        verbose_name_plural = 'dishes'
        ordering = ['name']


class MenuDish(Model):
    dish = ForeignKey(Dish, on_delete=models.CASCADE)
    service = ForeignKey(Service, on_delete=models.CASCADE)
    date = DateField()
    price = IntegerField()

    class Meta:
        unique_together = ['dish', 'service']
        verbose_name_plural = 'menu dishes'

    def __str__(self):
        return f'{self.dish}, {self.service} ({self.date})'


class ProductCategory(Model):
    name = TextField(max_length=100)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']


class Product(Model):
    name = TextField(max_length=100)
    price = IntegerField()
    category = ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='products')
    check_date = DateField(auto_now_add=True)


class ServiceProduct(Sellable, Model):
    service = ForeignKey(Service, on_delete=models.CASCADE)
    product = ForeignKey(Product, on_delete=models.PROTECT)
    price = IntegerField()

    class Meta:
        ordering = ['product']
        unique_together = ['service', 'product']

    def __str__(self):
        return '%s, %0.2f€ (%s)' % (self.product, self.price / 100, self.service.name)
