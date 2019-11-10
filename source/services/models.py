from django.db import models as djm

from college.models import Building, Place
from store.models import Sellable


class Service(djm.Model):
    name = djm.CharField(max_length=64)
    place = djm.ForeignKey(Place, null=True, blank=True, on_delete=djm.SET_NULL)
    map_tag = djm.CharField(max_length=15)
    opening = djm.TimeField(null=True, blank=True)
    restaurant = djm.BooleanField()
    # For a bar this is the meal time, for other places this is a break
    lunch_start = djm.TimeField(null=True, blank=True)
    lunch_end = djm.TimeField(null=True, blank=True)
    closing = djm.TimeField(null=True, blank=True)
    open_saturday = djm.BooleanField(default=False)
    open_sunday = djm.BooleanField(default=False)

    class Meta:
        unique_together = ['name', 'place']
        ordering = ['name']

    def __str__(self):
        return "{} ({})".format(self.name, '-')


class Dish(djm.Model):
    name = djm.CharField(max_length=128)
    price = djm.IntegerField()

    class Meta:
        verbose_name_plural = 'dishes'
        ordering = ['name']


class MenuDish(djm.Model):
    dish = djm.ForeignKey(Dish, on_delete=djm.CASCADE)
    service = djm.ForeignKey(Service, on_delete=djm.CASCADE)
    date = djm.DateField()
    price = djm.IntegerField()

    class Meta:
        unique_together = ['dish', 'service']
        verbose_name_plural = 'menu dishes'

    def __str__(self):
        return f'{self.dish}, {self.service} ({self.date})'


MEAL_TIME = (
    (1, "Pequeno-almoço"),
    (2, "Lanche da manhã"),
    (3, "Almoço"),
    (4, "Lanche da tarde"),
    (5, "Jantar"),
)

MEAL_PART_TYPE = (
    (1, "Sopa"),
    (2, "Carne"),
    (3, "Peixe"),
    (4, "Vegetariano"),
    (5, "Prato"),
    (6, "Sobremesa"),
    (7, "Bebida"),
    (8, "Menu"),
)


class MealItem(djm.Model):
    name = djm.CharField(max_length=256)
    date = djm.DateField()
    time = djm.IntegerField(choices=MEAL_TIME)
    service = djm.ForeignKey(Service, on_delete=djm.CASCADE)
    meal_part_type = djm.IntegerField(choices=MEAL_PART_TYPE)
    sugars = djm.IntegerField(null=True, blank=True)
    fats = djm.IntegerField(null=True, blank=True)
    proteins = djm.IntegerField(null=True, blank=True)
    calories = djm.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'date', 'time', 'service', 'meal_part_type')

    def __str__(self):
        return f'{self.name}, {self.service} ({self.date}/{self.time})'


class ProductCategory(djm.Model):
    name = djm.CharField(max_length=128)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']


class Product(djm.Model):
    name = djm.CharField(max_length=128)
    price = djm.IntegerField()
    category = djm.ForeignKey(ProductCategory, on_delete=djm.PROTECT, related_name='products')
    check_date = djm.DateField(auto_now_add=True)


class ServiceProduct(Sellable, djm.Model):
    service = djm.ForeignKey(Service, on_delete=djm.CASCADE)
    product = djm.ForeignKey(Product, on_delete=djm.PROTECT)
    price = djm.IntegerField()

    class Meta:
        ordering = ['product']
        unique_together = ['service', 'product']

    def __str__(self):
        return '%s, %0.2f€ (%s)' % (self.product, self.price / 100, self.service.name)
