from datetime import date
from django.db import models
from django.db.models import Model, IntegerField, TextField, ForeignKey, DateTimeField, ManyToManyField, DateField

from college.models import Place, TurnInstance
from groups.models import Group
from users.models import User


class Event(Model):
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()
    announce_date = DateField(default=date.today)
    place = ForeignKey(Place, null=True, blank=True, on_delete=models.SET_NULL)
    users = ManyToManyField(User, through='EventUser')

    def __str__(self):
        return f'from {self.datetime_to_eventtime(self.start_datetime)} ' \
               f'to {self.datetime_to_eventtime(self.end_datetime)}'

    def interval(self):
        if self.start_datetime.day == self.end_datetime.day:
            return '%02d-%02d %02d:%02d - %02d:%02d' % (self.start_datetime.day, self.start_datetime.month,
                                                        self.start_datetime.hour, self.start_datetime.minute,
                                                        self.end_datetime.hour, self.end_datetime.minute)

        return '%02d-%02d %02d:%02d - %02d-%02d %02d:%02d' % (self.start_datetime.day, self.start_datetime.month,
                                                              self.start_datetime.hour, self.start_datetime.minute,
                                                              self.end_datetime.day, self.end_datetime.month,
                                                              self.end_datetime.hour, self.end_datetime.minute)

    @staticmethod
    def datetime_to_eventtime(datetime):  # TODO move me somewhere else
        return '%02d-%02d, %02d:%02d' % (datetime.day, datetime.month, datetime.hour, datetime.minute)


class EventUser(Model):
    event = ForeignKey(Event, on_delete=models.CASCADE)
    user = ForeignKey(User, on_delete=models.CASCADE)


class TurnEvent(Event):
    turn_instance = ForeignKey(TurnInstance, on_delete=models.CASCADE)


class Workshop(Model):
    name = TextField(max_length=100)
    description = TextField(max_length=4096, null=True, blank=True)
    creator = ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name', 'creator']

    def __str__(self):
        return self.name


class WorkshopEvent(Event):
    workshop = ForeignKey(Workshop, on_delete=models.CASCADE)
    capacity = IntegerField(null=True, blank=True)


class Party(Model):
    name = TextField(max_length=100)
    description = TextField(max_length=4096, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'parties'

    def __str__(self):
        return self.name


class PartyEvent(Event):
    party = ForeignKey(Party, on_delete=models.CASCADE)
    capacity = IntegerField(null=True, blank=True)
