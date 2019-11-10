import locale
import re
from datetime import datetime
import scrapy
import html2text
from bs4 import BeautifulSoup

from scrapper.canteen.items import MealItem

mdconverter = html2text.HTML2Text()
locale.setlocale(locale.LC_ALL, 'pt_PT.UTF-8')


class CanteenSpider(scrapy.Spider):
    name = "canteen-spider"
    start_urls = [
        'https://sas.unl.pt/alimentacao/cantina-da-faculdade-de-ciencias-e-tecnologia-fct/',
    ]

    allowed_domains = [
        'https://sas.unl.pt'
    ]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for day_element in soup.find(id='ementa-container').find_all(class_="day-slot"):
            date = datetime.strptime(
                day_element.find(class_='header').text.split(', ')[-1],
                "%d de %B de %Y")
            meals = day_element.find_all(class_="list")
            for meal in meals:
                meal_name = meal.previous_sibling.previous_sibling.text
                meal_type = meal_name_to_int(meal_name)
                if meal_type is None:
                    raise Exception()

                for row in meal.find_all(class_='row'):
                    cols = row.find_all(class_="list-col")
                    if len(cols) == 6:
                        meal_item_type = cols[0].text
                        meal_item_name = cols[1].text
                        sugars = cols[2].text
                        fats = cols[3].text
                        proteins = cols[4].text
                        calories = cols[5].text
                        sugars = int(float(sugars) * 10)
                        fats = int(float(fats) * 10)
                        proteins = int(float(proteins) * 10)
                        calories = int(float(calories) * 10)
                        cleaned_meal_item_name = re.sub('\(\d{1,2}\)', '', meal_item_name)
                        meal_item_type = meal_item_str_type_to_int(meal_item_type, cleaned_meal_item_name)

                        yield MealItem(
                            name=cleaned_meal_item_name,
                            date=date,
                            time=meal_type,
                            sugars=sugars,
                            fats=fats,
                            proteins=proteins,
                            calories=calories,
                            item_type=meal_item_type,
                        )
                    else:
                        print("Phuck")


def meal_name_to_int(name):
    if name == 'Almoço':
        return 2
    elif name == 'Snack':
        return 3
    elif name == 'Jantar':
        return 4


known_meat = {'carne', 'porco', 'vaca', 'frango', 'galinha', 'peru', 'perna', 'asa', 'peito', 'bacon'}
known_fish = {'peixe', 'pescada', 'bacalhau', 'filetes', 'atum', 'solha', 'douradinhos', 'marisco'}


def meal_item_str_type_to_int(type_str, name):
    name = name.lower()
    if type_str == 'Sopa':
        return 1
    elif type_str == 'Veg.':
        return 4
    elif type_str == 'Prato':
        for item in known_meat:
            if item in name:
                return 2
        for item in known_fish:
            if item in name:
                return 3
    return 5
