from dal import autocomplete
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from chat import models as m
from supernova.views import build_base_context


def index_view(request):
    context = build_base_context(request)
    context['pcode'] = "t_chat"
    context['title'] = "Salas de conversa"
    context['rooms'] = m.PublicRoom.objects.all()
    context['sub_nav'] = [
        {'name': 'Conversas', 'url': reverse('college:index')}]
    return render(request, 'chat/index.html', context)


def messages_view(request):
    context = build_base_context(request)
    context['pcode'] = "u_chat"
    context['title'] = f"Mensagens"
    context['conversations'] = m.Conversation.objects.filter().all()
    return render(request, 'chat/messages.html', context)


def room_view(request, room_name):
    room = get_object_or_404(m.PublicRoom.objects, identifier=room_name)
    context = build_base_context(request)
    context['pcode'] = "t_chat_room"
    context['title'] = f"Sala de conversa {room.name}"
    context['room'] = room
    context['sub_nav'] = [
        {'name': 'Conversas', 'url': reverse('college:index')},
        {'name': f'#{room_name}', 'url': request.get_raw_uri()},
    ]
    return render(request, 'chat/room.html', context)


class RoomAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = m.Room.objects.all()
        if self.q:
            qs = qs.filter(name__contains=self.q)
        return qs
