from django.contrib import admin

from planet.models import Post, Comment, PostVote, CommentVote

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostVote)
admin.site.register(CommentVote)
