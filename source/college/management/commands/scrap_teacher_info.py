from django.core.management.base import BaseCommand
from scrapy.settings import Settings

from scrapper.teachers.spider import TeacherSpider
from scrapy.crawler import CrawlerProcess
from scrapper.teachers import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        crawler_settings = Settings()
        crawler_settings.setmodule(settings)
        process = CrawlerProcess(crawler_settings)

        process.crawl(TeacherSpider)
        process.start()
