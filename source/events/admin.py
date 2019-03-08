from django.contrib import admin
from events.models import Workshop, Party, Event, EventUser, TurnEvent, WorkshopEvent, PartyEvent

admin.site.register(Workshop)
admin.site.register(Party)
admin.site.register(Event)
admin.site.register(EventUser)
admin.site.register(TurnEvent)
admin.site.register(WorkshopEvent)
admin.site.register(PartyEvent)
