from django.contrib import admin
from events.models import Workshop, Party, Event, EventUsers, TurnEvent, WorkshopEvent, PartyEvent

admin.site.register(Workshop)
admin.site.register(Party)
admin.site.register(Event)
admin.site.register(EventUsers)
admin.site.register(TurnEvent)
admin.site.register(WorkshopEvent)
admin.site.register(PartyEvent)
