from django.core.management.base import BaseCommand
from scrapy.settings import Settings

from scrapper.news.spider import NewsItemSpider
from scrapy.crawler import CrawlerProcess
from scrapper.news import settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            default=10,
            help="Number of days back in time to crawl",
            type=int
        )

    def handle(self, *args, **options):
        days = options['days']
        crawler_settings = Settings()
        crawler_settings.setmodule(settings)
        process = CrawlerProcess(crawler_settings)

        process.crawl(NewsItemSpider, days=days)
        process.start()
