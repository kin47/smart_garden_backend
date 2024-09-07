from django.urls import path
from . import views

urlpatterns = [
    path('', views.RegisterDeviceToken.as_view(), name='register_device_token'),
]
