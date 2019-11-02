from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.timezone import now

from events.models import Event, WorkshopEvent, PartyEvent
from supernova.views import build_base_context


def index(request):
    context = build_base_context(request)
    context['page'] = 'instance_turns'
    context['title'] = 'Eventos'
    context['events'] = Event.objects.filter(  # Only events starting from now, and excluding turn events
        start_datetime__gt=now(), turnevent__isnull=True).order_by('announce_date').reverse()[0:10]
    context['next_workshops'] = WorkshopEvent.objects.order_by('start_datetime')[0:10]
    context['next_parties'] = PartyEvent.objects.order_by('start_datetime')[0:10]
    context['sub_nav'] = [{'name': 'Eventos', 'url': reverse('events')}]
    return render(request, 'events/events.html', context)


def event(request, event_id):
    context = build_base_context(request)
    context['title'] = 'Evento '  # TODO
    context['page'] = 'instance_turns'
    event = get_object_or_404(Event, id=event_id)
    if hasattr(event, 'workshop'):
        return HttpResponseRedirect('index')  # TODO
    else:
        pass
