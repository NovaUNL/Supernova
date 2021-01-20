import re

import scrapy
from bs4 import BeautifulSoup

class_link_exp = re.compile("/fct/program/(\d+)/course/(\d+)(#.*)?$")
route_link_exp = re.compile("/fct/program/(\d+)(#.*)?$")


class CourseSpider(scrapy.Spider):
    name = 'unl'
    allowed_domains = ['unl.pt']
    start_urls = [
        'https://guia.unl.pt/pt/2020/fct',
    ]

    def parse(self, response):
        for course_link in response.css('.list-group-item>a::attr(href)').getall():
            yield scrapy.Request(response.urljoin(course_link), self.course_parse)

    def course_parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        name = soup.find(class_='content-header').text.strip()
        structure_root = soup.find(id='structure')
        if structure_root is None:
            return
        route_links = structure_root.find_all('a', href=route_link_exp)
        if len(route_links) > 0:
            return
        class_links = structure_root.find_all('a', href=class_link_exp)
        if len(class_links) > 0:
            results = []
            options = set()
            for semestral_table in structure_root.find_all('table'):
                semester_results = []
                semester = semestral_table.find(class_='text-center').text.strip()
                body = semestral_table.find('tbody')
                foot = semestral_table.find('tfoot')
                mandatory = foot is None
                for row in body.find_all('tr'):
                    if row.text.strip() == 'Opções':
                        mandatory = False
                        continue
                    try:
                        class_id = int(row.contents[1].text.strip())
                    except Exception:
                        class_id = None
                    class_name = row.contents[3].text.strip()
                    try:
                        class_url = row.find(href=class_link_exp).attrs['href'].strip()
                    except Exception:
                        class_url = None
                    ects = float(row.contents[5].text.strip())
                    if mandatory:
                        semester_results.append((class_id, class_name, class_url, ects))
                    else:
                        options.add((semester, class_id, class_name, class_url, ects))
                if len(semester_results):
                    results.append((semester, semester_results))
            print("########################")
            print(name)
            print(results)
            print(options)
            print("########################")

            print()
            return
        print("Uh oh")

        # for course_link in response.css('.list-group-item>a::attr(href)').getall():
        #     yield scrapy.Request(response.urljoin(course_link), self.parse)
