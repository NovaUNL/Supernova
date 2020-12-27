from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from supernova.views import build_base_context
from news import models as m


def index_view(request):
    """
    Lists news items with a pagination feature.
    """
    paginator = Paginator(m.NewsItem.objects.order_by('datetime').reverse(), 10)
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


def item_view(request, news_item_id):
    """
    Show a news item.
    :param news_item_id: The id of the news item
    """
    news_item = get_object_or_404(m.NewsItem, id=news_item_id)
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


def pinned_item_view(request, pinned_item_id):
    """
    Show a pinned news item in a simple page.
    :param pinned_item_id: The id of the pinned news item
    """
    item = get_object_or_404(m.PinnedNewsItem, id=pinned_item_id)
    context = build_base_context(request)
    context['pcode'] = 'c_news'
    context['title'] = item.title
    context['item'] = item
    return render(request, 'news/simple_item.html', context)
