from django.urls import path
from . import views

urlpatterns = [
    path('', views.GetNotification.as_view(), name='get_notification'),
    path('mark-as-read/<int:id>', views.MarkAsRead.as_view(), name='mark_as_read'),
]
