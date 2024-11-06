from django.urls import path
from . import views

urlpatterns = [
    path('', view=views.GetKits.as_view(), name='get-kits'),
    path('user-in-kit/<int:kit_id>', view=views.UserInKit.as_view(), name='user-in-kit'),
    path('search-user', view=views.SearchUser.as_view(), name='search-user'),
    path('add-user-to-kit/<int:kit_id>', view=views.AddUser.as_view(), name='add-user'),
]
