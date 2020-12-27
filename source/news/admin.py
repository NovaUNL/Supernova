from django.contrib import admin

from news import models as m

admin.site.register(m.NewsTag)
admin.site.register(m.NewsItem)
admin.site.register(m.NewsVote)
admin.site.register(m.PinnedNewsItem)
