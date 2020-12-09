from rest_framework import serializers

from chat import models as m


class ConversationUserSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    nickname = serializers.CharField()
    name = serializers.CharField(required=False, source='get_full_name')
    thumbnail = serializers.ImageField(source='picture_thumbnail')
    profile = serializers.URLField(source='get_absolute_url')

    class Meta:
        model = m.ConversationUser
        fields = ('id', 'nickname', 'name', 'thumbnail', 'profile', 'last_read_message')


class ConversationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    identifier = serializers.CharField(required=False)
    creation = serializers.DateTimeField()
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False, source='chat_type')
    lastActivity = serializers.DateTimeField(source='last_activity')
    users = ConversationUserSerializer(many=True)

    class Meta:
        model = m.Conversation
        fields = ('id', 'identifier', 'name', 'type', 'creation', 'users', 'lastActivity')


class SimpleConversationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    identifier = serializers.CharField(required=False)
    creation = serializers.DateTimeField()
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False, source='chat_type')
    lastActivity = serializers.DateTimeField(source='last_activity')
    userCount = serializers.IntegerField(source='users.count')

    class Meta:
        model = m.Conversation
        fields = ('id', 'identifier', 'name', 'type', 'creation', 'userCount', 'lastActivity')


class SimplePrivateRoomSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    creation = serializers.DateTimeField()


class SimplePublicRoomSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    identifier = serializers.CharField()
    name = serializers.CharField()
    creation = serializers.DateTimeField()


class SimpleDMConversationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    creation = serializers.DateTimeField()
    nicknames = serializers.ListField(source='users__nickname')


class MessageAuthorSerializer(serializers.Serializer):
    id = serializers.CharField()
    nickname = serializers.CharField()
    url = serializers.CharField(source='get_absolute_url')


class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    creation = serializers.DateTimeField()
    content = serializers.CharField(required=False)
    # author = serializers.IntegerField(source='author.id') # TODO use this instead
    author = ConversationUserSerializer()
