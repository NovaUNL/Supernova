from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from kleep.views import build_base_context
from store.models import StoreItem


def index(request):
    context = build_base_context(request)
    context['title'] = 'Loja'
    context['items'] = StoreItem.objects.all()[0:50]
    context['sub_nav'] = [{'name': 'Artigos', 'url': reverse('store:all_items')}]
    return render(request, 'store/items.html', context)


def item(request, item_id):
    context = build_base_context(request)
    item = get_object_or_404(StoreItem, id=item_id)
    context['title'] = item.name
    context['item'] = item
    context['sub_nav'] = [{'name': 'Loja', 'url': reverse('store:all_items')},
                          {'name': item.name, 'url': reverse('store:item', args=[item_id])}]
    return render(request, 'store/item.html', context)
