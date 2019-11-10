import scrapy
from scrapy_djangoitem import DjangoItem
from services.models import MealItem as DMealItem


class MealItem(DjangoItem):
    django_model = DMealItem
    name = scrapy.Field()
    date = scrapy.Field()
    time = scrapy.Field()
    sugars = scrapy.Field()
    fat = scrapy.Field()
    proteins = scrapy.Field()
    calories = scrapy.Field()
    item_type = scrapy.Field()