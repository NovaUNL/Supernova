import re

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Q

import settings
from users import models as m
from learning import models as learning

NETWORK_PROFILE_URL_REGEX = [
    re.compile(r'(http[s]?://)?(www\.)?gitlab\.com/(?P<username>\w+)[/]?$'),
    re.compile(r'(http[s]?://)?(www\.)?github\.com/(?P<username>\w+)[/]?$'),
    re.compile(r'(http[s]?://)?(www\.)?reddit\.com/u(ser)?/(?P<username>.*)\b[/]?$'),
    re.compile(r'^(?P<username>\w+#\w+)$'),  # Discord
    re.compile(r'(http[s]?://)?([\w.]+)?linkedin\.com/in/(?P<username>.+)$'),
    re.compile(r'(http[s]?://)twitter\.com/(?P<username>.+)$'),
    re.compile(r'(http[s]?://)plus.google\.com/\+(?P<username>\w+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)?(www\.)?facebook\.\w+/(?P<username>\w+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)vimeo\.com/(?P<username>\w+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)(www\.)?youtube\.com/channel/(?P<username>\w+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)(?P<username>\w+)\.deviantart\.com(/(\?.*)?)?'),
    re.compile(r'(http[s]?://)(www\.)?instagram\.com/(p/)?(?P<username>[\w-]+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)(www\.)?flickr\.com/photos/(?P<username>[\w@-]+)(/(\?.*)?)??$'),
    re.compile(r'(http[s]?://)(www\.)?myanimelist\.net/profile/(?P<username>[\w-]+)(/(\?.*)?)?$'),
    re.compile(r'(http[s]?://)(www\.)?imdb\.com/user/(?P<username>[\w-]+)(/(\?.*)?)?$')
]

NETWORK_URLS = [
    "https://gitlab.com/{}",
    "https://github.com/{}",
    "https://reddit.com/user/{}",
    "{}",  # Discord
    "https://linkedin.com/in/{}",
    "https://twitter.com/{}",
    "https://plus.google.com/+{}",
    "https://facebook.com/{}",
    "https://vimeo.com/{}",
    "https://youtube.com/channel/{}",
    "https://{}.deviantart.com/",
    "https://instagram.com/p/{}",
    "https://flickr.com/photos/{}",
    "https://myanimelist.net/profile/{}",
    "https://imdb.com/user/{}"
]


def get_students(user):
    primary_students, secondary_students = [], []
    for student in user.students.all():
        if student.first_year is not None and student.last_year >= settings.COLLEGE_YEAR:
            primary_students.append(student)
        else:
            secondary_students.append(student)
    return primary_students, secondary_students


def get_network_identifier(network: int, link: str):
    if network >= len(NETWORK_PROFILE_URL_REGEX):
        raise Exception()  # TODO proper django exception
    return NETWORK_PROFILE_URL_REGEX[network].match(link).group('username')


def get_network_url(network: int, identifier: str):
    if network >= len(NETWORK_PROFILE_URL_REGEX):
        raise Exception()  # TODO proper django exception
    return NETWORK_URLS[network].format(identifier)


def get_user_stats(user):
    stats = cache.get(f'user_{user.id}_stats')
    if not None:
        stats = dict()
        stats['exercise_count'] = user.contributed_exercises.count()
        stats['question_count'] = learning.Question.objects.filter(user=user).count()
        stats['answer_count'] = answer_count = learning.QuestionAnswer.objects.filter(user=user).count()
        stats['accepted_answer_count'] = \
            accepted_count = learning.QuestionAnswer.objects.filter(user=user, accepted=True).count()
        stats['accepted_answer_percentage'] = 100 if answer_count == 0 \
            else int((accepted_count / answer_count) * 100)
        stats['edited_section_count'] = learning.Section.objects.filter(log_entries__author=user).distinct().count()
        stats['invited_count'] = m.Invite.objects.filter(issuer=user).exclude(registration=None).count()
        cache.set(f'user_{user.id}_stats', stats, timeout=60 * 60 * 24)
    return stats
