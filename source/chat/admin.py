from django.contrib import admin
from chat import models as m

admin.site.register(m.Conversation)
admin.site.register(m.ConversationUser)
admin.site.register(m.GroupExternalConversation)
admin.site.register(m.GroupInternalConversation)
admin.site.register(m.Message)
admin.site.register(m.Room)
