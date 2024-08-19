from django.urls import path
from . import views

urlpatterns = [
    path('', view=views.GetStores.as_view(), name='store'),
]
