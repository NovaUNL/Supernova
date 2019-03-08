from django.contrib import admin

from news.models import NewsTag, NewsItem, NewsVote

admin.site.register(NewsTag)
admin.site.register(NewsItem)
admin.site.register(NewsVote)
