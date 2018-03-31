from django.contrib import admin

from news.models import NewsTag, NewsItem, VoteType, NewsVote

admin.site.register(NewsTag)
admin.site.register(NewsItem)
admin.site.register(VoteType)
admin.site.register(NewsVote)
