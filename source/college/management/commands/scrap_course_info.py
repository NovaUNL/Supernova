from django.core.management.base import BaseCommand

from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from scrapper.courses.spider import CourseSpider
from scrapper.courses import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        crawler_settings = Settings()
        crawler_settings.setmodule(settings)
        process = CrawlerProcess(crawler_settings)

        process.crawl(CourseSpider)
        process.start()
