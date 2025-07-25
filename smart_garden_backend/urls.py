from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/store/', include('store.urls')),
    path('api/v1/notification/', include('notification.urls')),
    path('api/v1/device-token', include('device_token.urls')),
    path('api/v1/disease_detection/', include('disease_detection.urls')),
    path('api/v1/admin/user-management/', include('user_management.urls')),
    path('api/v1/admin/kit-management/', include('kit_management.urls')),
    path('api/v1/kit/', include('kit.urls')),
    path('api/v1/chat/', include('chat.urls')),
]
