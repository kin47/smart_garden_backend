from django.urls import path
from . import views

urlpatterns = [
    path('', view=views.UserManagement.as_view(), name='user_management'),
    path('get-info/<int:id>', view=views.GetUserInfo.as_view(), name='get_user_info'),
    path('update/<int:id>', view=views.UpdateUserInformation.as_view(), name='update_user'),
]
