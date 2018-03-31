from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from kleep.views import build_base_context
from news.models import NewsItem


def index(request):
    context = build_base_context(request)
    context['title'] = 'Notícias'
    context['news'] = NewsItem.objects.order_by('datetime').reverse()[0:10]
    context['sub_nav'] = [{'name': 'Noticias', 'url': reverse('news_index')}]
    return render(request, 'news/recent.html', context)


def item(request, news_item_id):
    context = build_base_context(request)
    news_item = get_object_or_404(NewsItem, id=news_item_id)
    context['page'] = 'instance_turns'
    context['title'] = 'Notícia:' + news_item.title
    context['news_item'] = news_item
    context['sub_nav'] = [{'name': 'Noticias', 'url': reverse('news_index')},
                          {'name': news_item.title, 'url': reverse('news_item', args=[news_item_id])}]
    return render(request, 'news/item.html', context)