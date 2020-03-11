from django.db import models as djm

from college.models import Building, Place


def service_pic_path(service, filename):
    return f's/{service.id}/pic.{filename.split(".")[-1].lower()}'


class Service(djm.Model):
    """
    | An entity which presents a service.
    | The provided service can be a physical good, an information service or anything else,
      as long as it has a physical presence.
    """
    #: Name of the service provider entity
    name = djm.CharField(max_length=128)
    #: Shortened version of the name
    abbreviation = djm.CharField(max_length=64)
    #: Place where the main instance of this service is
    place = djm.ForeignKey(Place, null=True, blank=True, on_delete=djm.SET_NULL)
    #: Tag that represents this service in the campus map.
    map_tag = djm.CharField(max_length=15)
    #: Picture that represents this service
    picture = djm.ImageField(upload_to=service_pic_path, null=True, blank=True)

    ACADEMIC = 0
    MEAL_PLACE = 1
    LIBRARY = 2
    REPROGRAPHY = 3
    STORE = 4
    ATM = 5
    SECURITY = 6
    OTHER = 100

    #: Enumeration of service types
    TYPE_CHOICES = (
        (ACADEMIC, "Serviço académico"),
        (MEAL_PLACE, "Restauração"),
        (LIBRARY, "Biblioteca"),
        (REPROGRAPHY, "Reprografia"),
        (STORE, "Loja"),
        (ATM, "Multibanco"),
        (SECURITY, "Segurança"),
        (OTHER, "Outro"),
    )
    #: Type which best describes this service. Enumerated by :py:attr:`TYPE_CHOICES`
    type = djm.IntegerField(choices=TYPE_CHOICES)

    class Meta:
        unique_together = ['name', 'place']
        ordering = ['name']

    def __str__(self):
        return "{} ({})".format(self.name, '-')


class ServiceScheduleEntry(djm.Model):
    """An entry on a service's schedule."""
    #: Service this entry refers to
    service = djm.ForeignKey(Service, on_delete=djm.CASCADE, related_name='schedule')
    #: A textual designation for this entry (such as "lunch")
    designation = djm.CharField(max_length=128, blank=True, null=True)
    #: Entry start time
    start = djm.TimeField()
    #: Entry end time
    end = djm.TimeField()
    #: Enumeration of weekday choices. Some include multiple days.
    WEEKDAY_CHOICES = (
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
        (7, 'Dias úteis'),
    )
    #: Weekdays enumerated by :py:attr:`WEEKDAY_CHOICES`
    weekday = djm.IntegerField(choices=WEEKDAY_CHOICES)

    class Meta:
        unique_together = ('service', 'weekday', 'start', 'designation')
        ordering = ('service', 'weekday', 'start', 'designation')
        verbose_name_plural = "Service schedule entries"


class MealItem(djm.Model):
    """One available meal item at a given meal in some service."""
    #: Service which offers this item
    service = djm.ForeignKey(Service, on_delete=djm.CASCADE, related_name='meal_items')
    #: Item verbose name
    name = djm.CharField(max_length=256)
    #: Date on which the item is going to available
    date = djm.DateField()
    #: Enumeration of possible meal times
    MEAL_TIME = (
        (0, "Pequeno-almoço"),
        (1, "Lanche da manhã"),
        (2, "Almoço"),
        (3, "Lanche da tarde"),
        (4, "Jantar"),
    )
    #: | Time of the day at which this meal is going to be offered.
    #: | Not literal time, enumerated by :py:attr:`MEAL_TIME`
    time = djm.IntegerField(choices=MEAL_TIME)

    #: Enumeration of types of meal items
    MEAL_PART_TYPE = (
        (0, "Sopa"),
        (1, "Carne"),
        (2, "Peixe"),
        (3, "Vegetariano"),
        (4, "Prato"),
        (5, "Sobremesa"),
        (6, "Bebida"),
        (7, "Menu"),
    )
    #: Type of meal item (meat, fish, soup, drink, ...). Enumerated by :py:attr:`MEAL_PART_TYPE`
    meal_part_type = djm.IntegerField(choices=MEAL_PART_TYPE)
    #: Sugar grams in tenths of gram
    sugars = djm.IntegerField(null=True, blank=True)
    #: Fat grams in tenths of gram
    fats = djm.IntegerField(null=True, blank=True)
    #: Protein grams in tenths of gram
    proteins = djm.IntegerField(null=True, blank=True)
    #: Calories grams in tenths of kcal
    calories = djm.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ()
        unique_together = ('name', 'date', 'time', 'service', 'meal_part_type')

    def __str__(self):
        return f'{self.name}, {self.service} ({self.date}/{self.time})'


class ProductCategory(djm.Model):
    """A generic category for products"""
    #: The name of the category
    name = djm.CharField(max_length=128)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('name',)


class Product(djm.Model):
    """A physical product or abstract one such as a service; which is found within some campus service."""
    #: Service where this product is
    service = djm.ForeignKey(Service, on_delete=djm.CASCADE, related_name='products')
    #: Product name
    name = djm.CharField(max_length=128)
    #: Price in cents
    price = djm.IntegerField()
    #: Category which holds this product
    category = djm.ForeignKey(ProductCategory, on_delete=djm.PROTECT, related_name='products')
    #: Availability
    has_stock = djm.BooleanField(default=True)

    class Meta:
        ordering = ('service', 'category', 'name', 'price')
        unique_together = ('service', 'name')

    def __str__(self):
        return '%s, %0.2f€ (%s)' % (self.name, self.price / 100, self.service.name)
