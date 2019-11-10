from services.models import MealItem, Service


class CanteenPipeline(object):
    def process_item(self, item, spider):
        name = item['name']
        date = item['date']
        time = item['time']
        canteen = Service.objects.filter(name="Cantina").first()
        existing = MealItem.objects.filter(name=name, date=date, time=time, service=canteen).first()
        if existing is None:
            new_item = MealItem(
                service=canteen,
                name=name,
                date=date,
                time=time,
                meal_part_type=item['item_type'],
                sugars=item['sugars'],
                fats=item['fats'],
                proteins=item['proteins'],
                calories=item['calories']
            )
            new_item.save()
        else:
            existing.meal_part_type = item['item_type']
            existing.save()
