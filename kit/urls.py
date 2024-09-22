from django.urls import path
from . import views

urlpatterns = [
    path('', view=views.GetKits.as_view(), name='kit'),
]
