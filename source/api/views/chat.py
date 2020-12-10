from django.db.models import Count
from rest_framework import authentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.serializers import chat as serializers

from chat import models as chat
from users import models as users


@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
def chat_info(request, chat_id):
    conversation = get_object_or_404(chat.Conversation, id=chat_id)
    if not conversation.has_access(request.user):
        raise PermissionDenied()
    serialized = serializers.ConversationSerializer(conversation)
    return Response(serialized.data)

@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
def chat_presence(request):
    conversations = chat.Conversation.objects\
        .annotate(message_count=Count('messages'))\
        .filter(users=request.user, message_count__gt=0) \
        .order_by('last_activity') \
        .reverse() \
        .all()
    serialized = serializers.ConversationSerializer(conversations, many=True)
    return Response(serialized.data)


@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
def chat_history(request, chat_id):
    conversation = get_object_or_404(chat.Conversation, id=chat_id)
    if not conversation.has_access(request.user):
        raise PermissionDenied()

    if 'to' in request.GET:
        try:
            major = chat.Message.objects.get(id=int(request.GET['to']), conversation=conversation)

            messages = chat.Message.objects \
                           .filter(conversation=conversation, id__lt=major.id) \
                           .select_related('author') \
                           .order_by('creation') \
                           .reverse()[:50]
        except (chat.Message.DoesNotExist, ValueError):
            return Response({'field': 'to_id', 'error': 'unknown message'}, status=400)

    else:
        messages = chat.Message.objects \
                       .filter(conversation=conversation) \
                       .select_related('author') \
                       .order_by('creation') \
                       .reverse()[:50]

    serialized = serializers.MessageSerializer(messages, many=True)
    return Response(serialized.data)


@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
def chat_query(request):
    if 'q' not in request.GET:
        return Response({"results": []})
    query = request.GET['q']
    assert isinstance(query, str)

    # dms = chat.DMChat.objects \
    #     .filter(users=request.user, users__nickname__icontains=query) \
    #     .order_by('messages__creation') \
    #     .reverse() \
    #     .all()
    private_rooms = chat.PrivateRoom.objects \
        .filter(name__icontains=query, users=request.user) \
        .reverse() \
        .all()
    public_rooms = chat.PublicRoom.objects \
        .filter(name__icontains=query) \
        .reverse() \
        .all()

    # dm_conversation_data = serializers.SimpleConversationSerializer(dms, many=True).data
    private_rooms_data = serializers.SimpleConversationSerializer(private_rooms, many=True).data
    public_rooms_data = serializers.SimpleConversationSerializer(public_rooms, many=True).data

    user_matches = users.User.objects.filter(nickname__icontains=query).all()

    results = []
    # if len(dm_conversation_data) > 0:
    #     results.append({
    #         "text": "Utilizadores conhecidos",
    #         "children": map(
    #             lambda room: {**room, **{'text': room['name']}},
    #             dm_conversation_data)
    #     })
    if len(private_rooms_data) > 0:
        results.append({
            "text": "Salas privadas",
            "children": map(
                lambda room: {**room, **{'text': room['name']}},
                private_rooms_data)
        })
    if len(public_rooms_data) > 0:
        results.append({
            "text": "Salas públicas",
            "children": map(
                lambda room: {**room, **{'text': room['name']}},
                public_rooms_data)
        })
    if len(user_matches) > 0:
        results.append({
            "text": "Utilizadores",
            "children": map(
                lambda user: {'id': f'u_{user.id}', 'text': user.nickname},
                user_matches)
        })

    response = {"results": results}

    return Response(response)


@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
def dm_request(request, user_id):
    user = get_object_or_404(users.User, id=user_id)
    conversation = get_or_create_dm_chat(request.user, user)
    serialized = serializers.ConversationSerializer(conversation)
    return Response(serialized.data)


@api_view(['GET'])
@authentication_classes((authentication.SessionAuthentication, authentication.BasicAuthentication))
def chat_join_request(request, reference):
    try:
        conversation_id = int(reference)
        conversation = get_object_or_404(chat.Conversation.objects.prefetch_related('users'), id=conversation_id)
    except ValueError:
        if not reference.startswith('u_'):
            raise Exception()

        try:
            user_id = int(reference.lstrip('u_'))
            user = get_object_or_404(users.User, id=user_id)
            conversation = get_or_create_dm_chat(request.user, user)
        except ValueError:
            raise Exception()

    if not conversation.has_access(request.user):
        raise PermissionDenied()

    if request.user not in conversation.users.all():
        conversation.users.add(request.user)

    serialized = serializers.ConversationSerializer(conversation)
    return Response(serialized.data)


# FIXME this function needs mutual exclusivity
def get_or_create_dm_chat(from_user, to_user):
    try:
        conversation = chat.DMChat.objects.filter(users=from_user).get(users=to_user)
    except chat.DMChat.DoesNotExist:
        conversation = chat.DMChat.objects.create(creator=from_user)
        conversation.users.add(from_user)
        conversation.users.add(to_user)
    return conversation
