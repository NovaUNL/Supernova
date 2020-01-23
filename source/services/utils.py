from datetime import datetime, timedelta

from services.models import MealItem


def get_next_meal_items(service=None):
    now = datetime.now()
    if now.time().hour >= 21:  # Consider next day if dinner is over
        now = now + timedelta(hours=3)
    time = 2  # Lunch
    if now.weekday() == 5:  # Sunday
        day_offset = 2
    elif now.weekday() == 6:  # Saturday
        day_offset = 1
    else:
        day_offset = 0
        if now.time().hour >= 15:
            time = 4  # Dinner

    meal_date = (now + timedelta(days=day_offset)).date()
    if service is None:
        meal_items = MealItem.objects \
            .filter(service__name="Cantina", date=meal_date, time=time) \
            .order_by('meal_part_type')
    else:
        meal_items = MealItem.objects \
            .filter(service=service, date=meal_date, time=time) \
            .order_by('meal_part_type')

    meal_items = map(
        lambda meal_item: (
            meal_item.meal_part_type,
            meal_item.name,
            float(meal_item.sugars) / 10,
            float(meal_item.fats) / 10,
            float(meal_item.proteins) / 10,
            float(meal_item.calories) / 10),
        meal_items)
    return meal_items, meal_date, time
