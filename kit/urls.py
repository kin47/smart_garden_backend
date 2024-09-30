from django.urls import path
from . import views

urlpatterns = [
    path('control/<int:kit_id>', view=views.ControlKit.as_view(), name='control-kit'),
]
