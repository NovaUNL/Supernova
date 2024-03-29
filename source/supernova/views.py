from datetime import datetime
import random

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Q, F, Count
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from services.utils import get_next_meal_items
from supernova import models as m
from supernova import forms as f
from news import models as news
from college import models as college
from groups import models as groups
from learning import models as learning


def index(request):
    context = build_base_context(request)

    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    minutes = (now - midnight).seconds // 60

    context['title'] = "De universitários para universitários"
    context['news'] = news.NewsItem.objects.order_by('datetime').reverse()[0:6]

    changelog_last = cache.get(f'changelog_last')
    if changelog_last is None:
        changelog_last = m.Changelog.objects.order_by('date').reverse().first()
        cache.set('changelog_last', changelog_last, timeout=60 * 60)
    context['changelog'] = changelog_last

    context['meal_items'], context['meal_date'], time = get_next_meal_items()

    next_meal_items = cache.get(f'next_meal_items')
    if next_meal_items is None:
        next_meal_items = get_next_meal_items()
        cache.set('next_meal_items', next_meal_items, timeout=60 * 10)
    context['meal_items'], context['meal_date'], time = next_meal_items
    context['meal_name'] = 'Almoço' if time == 2 else 'Jantar'

    free_rooms = cache.get('free_rooms')
    if free_rooms is None:
        free_rooms = college.Room.objects \
            .annotate(shift_instances__end=F('shift_instances__start') + F('shift_instances__duration')) \
            .filter(unlocked=True) \
            .select_related('building') \
            .order_by('building__abbreviation', 'name') \
            .exclude(Q(shift_instances__start__lt=minutes + 5) & Q(shift_instances__end__gt=minutes)) \
            .distinct('building__abbreviation', 'name')
        cache.set('free_rooms', free_rooms, timeout=60)
    context['free_rooms'] = random.sample(set(free_rooms), min(10, len(free_rooms))) if len(free_rooms) > 0 else []

    metrics = cache.get('usage_metrics')
    if metrics is None:
        metrics = {
            'student_count': college.Student.objects.exclude(user=None).count(),
            'teacher_count': college.Teacher.objects.exclude(user=None).count(),
            'allowing_teacher_count': college.Teacher.objects \
                .exclude(file_consent=None) \
                .exclude(file_consent=college.ctypes.FileVisibility.NOBODY) \
                .count(),
            'pledge_count': m.SupportPledge.objects.filter(pledge_towards__gt=m.SupportPledge.INDEPENDENT).count()
        }
        cache.set('usage_metrics', metrics, timeout=60 * 5)
    context.update(metrics)

    group_activities = cache.get('group_activities')
    if group_activities is None:
        group_activities = groups.Activity.objects \
                               .select_related('group') \
                               .order_by('datetime') \
                               .reverse()[:5]
        cache.set('group_activities', group_activities, timeout=60 * 5)
    context['activities'] = group_activities

    recent_questions = cache.get('recent_questions')
    if recent_questions is None:
        recent_questions = learning.Question.objects \
                               .select_related('user') \
                               .prefetch_related('linked_classes', 'linked_exercises', 'linked_sections') \
                               .annotate(answer_count=Count('answers')) \
                               .order_by('timestamp') \
                               .reverse()[:5]
        cache.set('recent_questions', recent_questions, timeout=60 * 5)
    context['recent_questions'] = recent_questions

    pinned_news = cache.get('pinned_news')
    if pinned_news is None:
        pinned_news = news.PinnedNewsItem.objects.filter(active=True).order_by('title').all()
        cache.set('pinned_news', pinned_news, timeout=60 * 5)
    context['pinned_news'] = pinned_news

    context['message'] = settings.INDEX_MESSAGE
    context['matrix_url'] = settings.MATRIX_URL
    context['signal_url'] = settings.SIGNAL_URL
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


@login_required
def support_view(request):
    context = build_base_context(request)
    context['title'] = "Apoio"
    context['pledge'] = m.SupportPledge.objects.filter(user=request.user)
    context['pledges'] = m.SupportPledge.objects.all()
    pledges = list(m.SupportPledge.objects.values_list('pledge_towards', flat=True))
    context['pledge_count'] = len(pledges)
    independent, independent_supp, association_compl, association_repl = \
        pledges.count(m.SupportPledge.INDEPENDENT), pledges.count(m.SupportPledge.INDEPENDENT_SUPPORTED), \
        pledges.count(m.SupportPledge.ASSOCIATION_COMPLEMENT), pledges.count(m.SupportPledge.ASSOCIATION_REPLACEMENT)
    context['independent'], context['independent_supp'], context['association_compl'], context['association_repl'] = \
        independent, independent_supp, association_compl, association_repl

    if request.method == 'POST':
        form = f.SupportPledgeForm(request.POST)
        if form.is_valid():
            pledge = form.save(commit=False)
            pledge.user = request.user
            pledge.save()
    else:
        form = f.SupportPledgeForm()
    context['pledge_form'] = form
    return render(request, 'supernova/pledge.html', context)


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
    todavia podes ajudá-los preenchendo um <a href="%s">relatório de bug</a>.</p>''' % settings.GITLAB_URL
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
