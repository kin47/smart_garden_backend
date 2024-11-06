from django.urls import path
from . import views

urlpatterns = [
    path('get-chat-messages', views.GetChatMessages.as_view(), name='get_chat_messages'),
    path('send-message', views.SendMessage.as_view(), name='send_message'),
    path('get-chat-list', views.GetChatList.as_view(), name='get_chat_list'),
]
