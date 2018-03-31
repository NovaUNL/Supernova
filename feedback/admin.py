from django.contrib import admin

from feedback.models import Comment, FeedbackEntry, FeedbackEntryComment

admin.site.register(Comment)
admin.site.register(FeedbackEntry)
admin.site.register(FeedbackEntryComment)
