import re

from bs4 import BeautifulSoup
from scrapy import Request

from scrapper.teachers.items import TeacherItem
import scrapy

ext_re = re.compile(".*[Ee]xt.*")
rank_re = re.compile(".*(Professor|Investigador)*")
email_re = re.compile("[\w.]*@[\w.]*unl.pt")
title_re = re.compile(".*(docentes|professor|pessoas|investigadores|node|B614-74C1-2CF8).*")

class TeacherSpider(scrapy.Spider):
    name = "di-archive"
    start_urls = [
        'https://www.di.fct.unl.pt/departamento/pessoas/docentes',
        'https://www.dee.fct.unl.pt/pessoas/docentes',
        'https://www.dcea.fct.unl.pt/pessoas/docentes',
        'https://www.dcm.fct.unl.pt/pessoas/docentes',
        'https://www.dcr.fct.unl.pt/pessoas/docentes',
        'https://www.dcsa.fct.unl.pt/pessoas/docentes',
        'https://www.dct.fct.unl.pt/pessoas/docentes',
        'https://www.dq.fct.unl.pt/pessoas/docentes',
        'https://www.dm.fct.unl.pt/pessoas/docentes',
        'https://www.df.fct.unl.pt/pessoas/docentes',
        'https://www.demi.fct.unl.pt/pessoas/docentes',
        'https://www.dee.fct.unl.pt/pessoas/docentes',
        'https://www.dec.fct.unl.pt/pessoas/docentes',
        'https://www.dcv.fct.unl.pt/pessoas/docentes',
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
    ]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        teachers = soup.find_all('div', class_='views-row')
        for teacher in teachers:
            item = TeacherItem()

            name_wrapper = teacher.find(class_='views-field-title')
            if name_wrapper is None:
                continue
            name_link = name_wrapper.find('a', href=title_re)
            name = name_link.text.strip()
            url = response.urljoin(name_link.attrs['href'])

            ext_elem = teacher.find('strong', text=ext_re)
            if ext_elem is not None:
                try:
                    item['ext'] = int(ext_elem.parent.text.split(':')[-1].strip())
                except ValueError:
                    item['ext'] = int(ext_elem.parent.text.split(':')[-1].split('/')[0].strip())

            email = str(teacher.find(text=email_re)).strip()
            rank_elem = teacher.find('span', text=rank_re, class_="field-content")
            if rank_elem is not None:
                rank = rank_elem.text.strip()
            else:
                rank = None

            item['name'] = name
            item['url'] = url
            item['email'] = email
            item['rank'] = rank
            item['origin'] = response.url
            # print(f"{name}, {url}, {email}, {rank}")
            img_elem = teacher.find('img')
            img_link = img_elem.attrs['src']
            if 'no-photo' in img_link:
                yield item
            else:
                yield Request(img_link, self.parse_image, meta={'item': item})

    def parse_image(self, response):
        body = response.body
        item = response.meta['item']
        if body is not None and body != b'':
            item['image_data'] = body
            item['image_ext'] = response.url.split('.')[-1]
        yield item
