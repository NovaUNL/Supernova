from datetime import datetime
from scrapper.news.items import NewsItemItem
import scrapy
import html2text

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

    def parse(self, response):
        for link in response.css('ul.views-summary li a::attr(href)').getall():
            if 'fct.unl.pt/noticias' in response.url:
                yield response.follow(link, self.parse_month)

    def parse_month(self, response):
        for link in response.css('ul.views-summary li a::attr(href)'):
            if 'fct.unl.pt/noticias' in response.url:
                yield response.follow(link, self.parse_news)

        for link in response.css('div.item-list ul.pager a::attr(href)'):
            if 'fct.unl.pt/noticias' in response.url:
                yield response.follow(link, self.parse_month)

    def parse_news(self, response):
        for link in response.css('div.views-row a::attr(href)'):
            if 'fct.unl.pt/noticias' in response.url:
                yield response.follow(link, self.parse_newsitem)

    def parse_newsitem(self, response):
        # lang = 'en' if '/en/' in response.url else 'pt'
        if '/en/' in response.url:
            return
        item = NewsItemItem()
        item['title'] = response.css('h1.page-titles::text').get().strip()
        date = response.css('p.noticia-data::text').get()
        if date is not None:
            item['datetime'] = datetime.strptime(date.strip(), '%d-%m-%Y')
        else:
            item['datetime'] = None
        content = response.css('div.noticia-corpo').extract()[0]
        content = mdconverter.handle(content)
        item['content'] = content
        item['source'] = response.url
        item['cover_img'] = response.css('img.imagem-noticia::attr(src)').get()
        yield item
