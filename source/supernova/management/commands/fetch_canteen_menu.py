from django.core.management.base import BaseCommand
from scrapy.settings import Settings

from scrapper.canteen.spider import CanteenSpider
from scrapy.crawler import CrawlerProcess
from scrapper.canteen import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        crawler_settings = Settings()
        crawler_settings.setmodule(settings)
        process = CrawlerProcess(crawler_settings)

        process.crawl(CanteenSpider)
        process.start()
