from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from django.utils.timezone import make_aware
from scrapy import Request

from scrapper.news.items import NewsItemItem
import scrapy
import html2text
import logging as log

mdconverter = html2text.HTML2Text()


class NewsItemSpider(scrapy.Spider):
    name = "di-archive"
    start_urls = [
        'https://www.di.fct.unl.pt/noticias/arquivo',
        'https://www.dcea.fct.unl.pt/noticias/arquivo',
        'https://www.dcm.fct.unl.pt/noticias/arquivo',
        'https://www.dcr.fct.unl.pt/noticias/arquivo',
        'https://www.dcsa.fct.unl.pt/noticias/arquivo',
        'https://www.dct.fct.unl.pt/noticias/arquivo',
        'https://www.dq.fct.unl.pt/noticias/arquivo',
        'https://www.dm.fct.unl.pt/noticias/arquivo',
        'https://www.df.fct.unl.pt/noticias/arquivo',
        'https://www.demi.fct.unl.pt/noticias/arquivo',
        'https://www.dee.fct.unl.pt/noticias/arquivo',
        'https://www.dec.fct.unl.pt/noticias/arquivo',
        'https://www.dcv.fct.unl.pt/noticias/arquivo',
        'https://www.biblioteca.fct.unl.pt/noticias/arquivo',
        'https://www.fct.unl.pt/noticias/arquivo',
    ]

    allowed_domains = [
        'www.fct.unl.pt',
        'www.di.fct.unl.pt',
        'www.dcea.fct.unl.pt',
        'www.dcm.fct.unl.pt',
        'www.dcr.fct.unl.pt',
        'www.dcsa.fct.unl.pt',
        'www.dct.fct.unl.pt',
        'www.dq.fct.unl.pt',
        'www.dm.fct.unl.pt',
        'www.df.fct.unl.pt',
        'www.demi.fct.unl.pt',
        'www.dee.fct.unl.pt',
        'www.dec.fct.unl.pt',
        'www.dcv.fct.unl.pt',
        'www.biblioteca.fct.unl.pt'
    ]

    def __init__(self, days=None):
        super().__init__()
        if days is None:
            self.upto = datetime.now() - timedelta(days=10000)
        else:
            self.upto = datetime.now() - timedelta(days=days)

    def parse(self, response):
        for link in response.css('ul.views-summary li a::attr(href)').getall():
            if 'fct.unl.pt/noticias' in response.url:
                parts = link.split("/")
                year = int(parts[-1])
                if year < self.upto.year:
                    continue
                yield response.follow(link, self.parse_month)

    def parse_month(self, response):
        for link in response.css('ul.views-summary li a::attr(href)').getall():
            if 'fct.unl.pt/noticias' in response.url:
                parts = link.split("/")
                year, month = int(parts[-2]), int(parts[-1])
                if year < self.upto.year or (year == self.upto.year and month < self.upto.month):
                    continue
                yield response.follow(link, self.parse_news)

        for link in response.xpath('//ul[@class="views-summary"]//a[contains(@href, "/noticias/arquivo/")]/@href'):
            yield response.follow(link, self.parse_month)

    def parse_news(self, response):
        for link in response.xpath('//div[@class="views-field-title"]//a/@href').getall():
            if link.endswith('.pdf') or '/en/' in response.url:
                continue
            try:
                yield response.follow(link, self.parse_newsitem)
            except ValueError:
                log.warning("Bad news URL %s" % link.root)

    def parse_newsitem(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItemItem()
        if (title := response.css('h1.page-titles::text').get()) is not None:
            item['title'] = title.strip()
        else:
            log.warning("%s is not a news item" % response.url)
            return

        date_elem = soup.find('p', class_='noticia-data')
        if not hasattr(date_elem, "parent"):
            log.warning("Skipped %s" % response.url)
            return
        content_elem = date_elem.parent
        item['datetime'] = make_aware(datetime.strptime(date_elem.text.strip(), '%d-%m-%Y'))
        content = str(content_elem.find('div', class_="noticia-corpo"))
        content = mdconverter.handle(content).strip()
        item['content'] = content
        item['html'] = response.text
        item['source'] = response.url
        img_elem = content_elem.find('img', class_="imagem-noticia")
        if img_elem is None:
            yield item
        else:
            yield Request(img_elem.attrs['src'], self.parse_image, meta={'item': item})

    def parse_image(self, response):
        body = response.body
        item = response.meta['item']
        if body is not None and body != b'':
            item['image_data'] = body
            item['image_filename'] = response.url.split('/')[-1]
        yield item
