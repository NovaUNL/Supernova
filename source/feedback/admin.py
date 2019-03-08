from django.contrib import admin

from feedback.models import Comment, Entry, EntryComment

admin.site.register(Comment)
admin.site.register(Entry)
admin.site.register(EntryComment)
