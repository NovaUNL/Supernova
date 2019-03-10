from datetime import date
from django.db import models as djm

from college.models import Place, TurnInstance
from groups.models import Group
from users.models import User


class Event(djm.Model):
    start_datetime = djm.DateTimeField()
    end_datetime = djm.DateTimeField()
    announce_date = djm.DateField(default=date.today)
    place = djm.ForeignKey(Place, null=True, blank=True, on_delete=djm.SET_NULL)
    users = djm.ManyToManyField(User, through='EventUser')

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


class EventUser(djm.Model):
    event = djm.ForeignKey(Event, on_delete=djm.CASCADE)
    user = djm.ForeignKey(User, on_delete=djm.CASCADE)


class TurnEvent(Event):
    turn_instance = djm.ForeignKey(TurnInstance, on_delete=djm.CASCADE)


class Workshop(djm.Model):
    name = djm.CharField(max_length=256)
    description = djm.TextField(max_length=4096, null=True, blank=True)
    creator = djm.ForeignKey(Group, null=True, blank=True, on_delete=djm.CASCADE)

    class Meta:
        unique_together = ['name', 'creator']

    def __str__(self):
        return self.name


class WorkshopEvent(Event):
    workshop = djm.ForeignKey(Workshop, on_delete=djm.CASCADE)
    capacity = djm.IntegerField(null=True, blank=True)


class Party(djm.Model):
    name = djm.CharField(max_length=128)
    description = djm.TextField(max_length=4096, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'parties'

    def __str__(self):
        return self.name


class PartyEvent(Event):
    party = djm.ForeignKey(Party, on_delete=djm.CASCADE)
    capacity = djm.IntegerField(null=True, blank=True)
