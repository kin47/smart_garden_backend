from django.urls import path
from . import views

urlpatterns = [
    path('', view=views.UserManagement.as_view(), name='user_management'),
    path('update/<int:id>', view=views.UpdateUserInformation.as_view(), name='update_user'),
]
