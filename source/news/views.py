from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from supernova.views import build_base_context
from news.models import NewsItem


def index(request):
    paginator = Paginator(NewsItem.objects.order_by('datetime').reverse(), 10)
    p = 1
    if 'p' in request.GET:
        try:
            p = int(request.GET['p'])
        except ValueError:
            pass
    p = max(min(p, paginator.num_pages), 0)
    page = paginator.page(p)

    context = build_base_context(request)
    context['pcode'] = 'c_news'
    context['title'] = 'Notícias'
    context['page'] = page
    context['paginator'] = paginator
    context['sub_nav'] = [{'name': 'Noticias', 'url': reverse('news:index')}]
    return render(request, 'news/list.html', context)


def item(request, news_item_id):
    news_item = get_object_or_404(NewsItem, id=news_item_id)
    context = build_base_context(request)
    context['pcode'] = 'c_news_item'
    context['title'] = 'Notícia:' + news_item.title
    if len(news_item.title) > 50:
        short_title = news_item.title[:50] + " ..."
    else:
        short_title = news_item.title
    context['news_item'] = news_item
    context['sub_nav'] = [
        {'name': 'Noticias', 'url': reverse('news:index')},
        {'name': short_title, 'url': reverse('news:item', args=[news_item_id])}]
    return render(request, 'news/item.html', context)
