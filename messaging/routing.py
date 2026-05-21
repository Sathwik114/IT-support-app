from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/task-chat/(?P<task_id>\d+)/$', consumers.TaskChatConsumer.as_asgi()),
    re_path(r'ws/typing/$', consumers.TypingConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
