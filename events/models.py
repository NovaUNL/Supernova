from datetime import date
from django.db import models
from django.db.models import Model, IntegerField, TextField, ForeignKey, DateTimeField, ManyToManyField, DateField

from college.models import Place, TurnInstance
from groups.models import Group
from kleep.models import KLEEP_TABLE_PREFIX, Profile


class Event(Model):
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()
    announce_date = DateField(default=date.today)
    classroom = ForeignKey(Place, null=True, blank=True, on_delete=models.SET_NULL)
    users = ManyToManyField(Profile, through='EventUsers')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'events'

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


class EventUsers(Model):
    event = ForeignKey(Event, on_delete=models.CASCADE)
    user = ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'event_users'


class TurnEvent(Event):
    turn_instance = ForeignKey(TurnInstance, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'turn_events'


class Workshop(Model):
    name = TextField(max_length=100)
    description = TextField(max_length=4096, null=True, blank=True)
    capacity = IntegerField(null=True, blank=True)
    creator = ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'workshops'

    def __str__(self):
        return self.name


class WorkshopEvent(Event):
    workshop = ForeignKey(Workshop, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'workshop_events'


class Party(Model):
    name = TextField(max_length=100)
    description = TextField(max_length=4096, null=True, blank=True)
    capacity = IntegerField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'parties'

    def __str__(self):
        return self.name


class PartyEvent(Event):
    party = ForeignKey(Party, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'party_events'
