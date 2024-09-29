from django.urls import path
from . import views

urlpatterns = [
    path('login', view=views.Login.as_view(), name='login'),
    path('register', view=views.Register.as_view(), name='register'),
    path('logout', view=views.Logout.as_view(), name='logout'),
    path('me', view=views.Me.as_view(), name='me'),
    path('update-info', view=views.UpdateInfo.as_view(), name='update-info'),
    path('resend', views.AccountVerification.as_view(), name='resend'),
    path('activate/<uidb64>/<token>', views.AccountVerification.activate, name='activate')
]
