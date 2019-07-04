from scrapy_djangoitem import DjangoItem
from news.models import NewsItem


class NewsItemItem(DjangoItem):
    django_model = NewsItem
