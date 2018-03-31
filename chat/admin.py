from django.contrib import admin
from chat.models import Conversation, Message, ConversationUser, GroupExternalConversation, GroupInternalConversation

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(ConversationUser)
admin.site.register(GroupExternalConversation)
admin.site.register(GroupInternalConversation)
