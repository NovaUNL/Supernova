import reversion
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

import settings
from supernova.views import build_base_context
from feedback import forms as f
from feedback import models as m


def suggestion_index_view(request):
    context = build_base_context(request)
    context['recent_objects'] = \
        m.Suggestion.objects \
            .select_related('user') \
            .order_by('timestamp') \
            .reverse()[:50]
    context['popular_objects'] = \
        m.Suggestion.objects \
            .order_by(F('upvotes') + F('downvotes'), 'timestamp') \
            .select_related('user') \
            .reverse()[:50]
    context['title'] = 'Sugestões'
    context['pcode'] = "c_feedback"
    if request.user.has_perm('feedback.add_suggestion'):
        context['create_url'] = reverse('feedback:suggestion_create')
    context['sub_nav'] = [{'name': 'Sugestões', 'url': reverse('feedback:index')}]
    return render(request, 'supernova/recent_and_popular_lists.html', context)


def suggestion_view(request, suggestion_id):
    context = build_base_context(request)
    suggestion = get_object_or_404(m.Suggestion, activity_id=suggestion_id)
    context['title'] = f"Sugestão: {suggestion.title}"
    context['pcode'] = "c_feedback"
    context['suggestion'] = suggestion
    context['sub_nav'] = [{'name': 'Sugestões', 'url': reverse('feedback:index')},
                          {'name': suggestion.title, 'url': reverse('feedback:suggestion', args=[suggestion_id])}]
    return render(request, 'feedback/suggestion.html', context)


@login_required
@permission_required('feedback.add_suggestion')
def suggestion_create_view(request, content_type_id=None, object_id=None):
    obj = None
    if object_id is not None:
        try:
            object_type = ContentType.objects.get_for_id(content_type_id)
            if object_type.natural_key() not in settings.SUGGESTABLE_ENTITIES:
                raise Exception()
            obj = object_type.get_object_for_this_type(id=object_id)
        except:
            return Http404()

    if request.method == 'POST':
        form = f.SuggestionForm(request.POST)
        if form.is_valid():
            with reversion.create_revision():
                suggestion = form.save(commit=False)
                suggestion.user = request.user
                if obj is not None:
                    suggestion.towards_object = obj
                suggestion.save()
                return HttpResponseRedirect(reverse('feedback:suggestion', args=[suggestion.activity_id]))
    else:
        form = f.SuggestionForm()
    context = build_base_context(request)
    context['form'] = form
    context['object'] = obj
    context['title'] = f"Nova sugestão"
    context['pcode'] = "c_feedback"
    context['sub_nav'] = [{'name': 'Sugestões', 'url': reverse('feedback:index')},
                          {'name': "Nova", 'url': reverse('feedback:suggestion_create')}]
    return render(request, 'feedback/suggestion_create.html', context)


@login_required
@permission_required('feedback.add_review')
def review_create_view(request, content_type_id, object_id):
    try:
        object_type = ContentType.objects.get_for_id(content_type_id)
        if object_type.natural_key() not in settings.REVIEWABLE_ENTITIES:
            raise Exception()
        obj = object_type.get_object_for_this_type(id=object_id)
    except:
        return Http404()

    if request.method == 'POST':
        form = f.ReviewForm(request.POST)
        if form.is_valid():
            with reversion.create_revision():
                review = form.save(commit=False)
                review.content_object = obj
                review.user = request.user
                review.save()
            return redirect(obj.get_absolute_url())
    else:
        form = f.ReviewForm()
    context = build_base_context(request)
    context['form'] = form
    context['title'] = f"Nova avaliação a {obj}"
    context['pcode'] = "c_feedback_review"
    context['sub_nav'] = [{'name': 'Avaliação', 'url': reverse('feedback:index')},
                          {'name': "Nova", 'url': reverse('feedback:suggestion_create')}]
    return render(request, 'feedback/review_create.html', context)
