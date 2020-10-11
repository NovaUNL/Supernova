from datetime import datetime
import random

from django.core.cache import cache
from django.db.models import Q, F, Count
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

import settings
from scrapper.boinc import boincstats
from services.utils import get_next_meal_items
from supernova import models as m
from news import models as news
from college import models as college
from groups import models as groups
from learning import models as learning


def index(request):
    context = build_base_context(request)

    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    minutes = (now - midnight).seconds // 60

    context['title'] = "Perfeição nanométrica"
    context['news'] = news.NewsItem.objects.order_by('datetime').reverse()[0:6]
    context['changelog'] = m.Changelog.objects.order_by('date').reverse().first()
    context['meal_items'], context['meal_date'], time = get_next_meal_items()
    context['meal_name'] = 'Almoço' if time == 2 else 'Jantar'
    boinc_users = boincstats.get_team_users(2068385380)
    boinc_users.sort(key=lambda x: -x['weekly'])
    context['boinc_users'] = boinc_users[:3]
    boinc_projects = boincstats.get_team_projects(2068385380)
    boinc_projects.sort(key=lambda x: -x['weekly'])
    context['boinc_projects'] = boinc_projects[:3]

    free_rooms = college.Room.objects \
        .annotate(shift_instances__end=F('shift_instances__start') + F('shift_instances__duration')) \
        .filter(unlocked=True) \
        .select_related('building') \
        .order_by('building__abbreviation', 'name') \
        .exclude(Q(shift_instances__start__lt=minutes) & Q(shift_instances__end__gt=minutes)) \
        .distinct('building__abbreviation', 'name')
    context['free_rooms'] = random.sample(set(free_rooms), min(10, len(free_rooms))) if len(free_rooms) > 0 else []

    context['activities'] = \
        groups.Activity.objects \
            .select_related('group') \
            .order_by('datetime') \
            .reverse()[:5]
    context['recent_questions'] = \
        learning.Question.objects \
            .select_related('user') \
            .prefetch_related('linked_classes', 'linked_exercises', 'linked_sections') \
            .annotate(answer_count=Count('answers')) \
            .order_by('timestamp') \
            .reverse()[:5]
    context['message'] = settings.INDEX_MESSAGE
    context['matrix_url'] = settings.MATRIX_URL
    context['mastodon_url'] = settings.MASTODON_URL
    context['telegram_url'] = settings.TELEGRAM_URL
    context['gitlab_url'] = settings.GITLAB_URL
    return render(request, 'supernova/index.html', context)


def changelog_view(request):
    context = build_base_context(request)
    context['title'] = "Alterações"
    context['changelog'] = m.Changelog.objects.order_by('date').reverse().all()
    context['sub_nav'] = [{'name': 'Alterações', 'url': reverse('news:index')}]
    return render(request, 'supernova/changes.html', context)


def bad_request_view(request, exception=None):
    context = build_base_context(request)
    context['title'] = context['msg_title'] = 'Mau pedido'
    context['msg_content'] = 'Fez um pedido inválido.'
    return render(request, "supernova/message.html", context, status=400)


def permission_denied_view(request, exception=None):
    context = build_base_context(request)
    context['title'] = context['msg_title'] = 'Sem permissões'
    context['msg_content'] = 'Não tem permissões para aceder a este conteúdo.'
    return render(request, "supernova/message.html", context, status=403)


def page_not_found_view(request, exception=None):
    context = build_base_context(request)
    context['title'] = context['msg_title'] = 'Não encontrado'
    context['msg_content'] = 'O conteúdo solicitado não foi encontrado.'
    return render(request, "supernova/message.html", context, status=404)


def error_view(request, exception=None):
    context = build_base_context(request)
    context['title'] = context['msg_title'] = 'Erro'
    context['msg_content'] = '''<p>Houve um erro a responder ao pedido.</p>
    <p>Um exercito de estagiários mal pagos saberá deste erro,
    todavia podes ajuda-los preenchendo um <a href="%s">relatório de bug</a>.</p>''' % settings.GITLAB_URL
    return render(request, "supernova/message.html", context, status=500)


def build_base_context(request):
    if not request.user.is_anonymous:
        request.user.last_activity = timezone.now()
        request.user.save(update_fields=['last_activity'])
    catchphrases = cache.get('catchphrases')
    if catchphrases is None:
        catchphrases = list(m.Catchphrase.objects.all())
        if len(catchphrases) == 0:
            catchphrases = ['']
        cache.set('catchphrases', catchphrases, timeout=3600 * 24)
    base_context = {
        'disable_auth': False,
        'sub_nav': None,
        'catchphrase': random.choice(catchphrases)
    }
    return base_context
