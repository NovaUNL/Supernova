from django.core.management.base import BaseCommand
from scrapy.settings import Settings

from scrapper.news.spider import NewsItemSpider
from scrapy.crawler import CrawlerProcess
from scrapper.news import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        crawler_settings = Settings()
        crawler_settings.setmodule(settings)
        process = CrawlerProcess(crawler_settings)

        process.crawl(NewsItemSpider)
        process.start()
