from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from planet.models import Post
from kleep.views import build_base_context


def index(request):
    context = build_base_context(request)
    context['title'] = 'Planeta'
    context['planet'] = Post.objects.order_by('datetime').reverse()[0:10]
    context['sub_nav'] = [{'name': 'Planeta', 'url': reverse('planet')}]
    return render(request, 'kleep/TODO.html', context)


def item(request, post_id):
    context = build_base_context(request)
    post = get_object_or_404(Post, id=post_id)
    context['title'] = post.name
    context['planet'] = Post.objects.order_by('datetime').reverse()[0:10]
    context['sub_nav'] = [{'name': 'Planeta', 'url': reverse('planet_index')},
                          {'name': post.name, 'url': reverse('planet_post', args=[post_id])}]
    return render(request, 'kleep/TODO.html', context)
