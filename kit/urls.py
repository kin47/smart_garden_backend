from django.urls import path
from . import views

urlpatterns = [
    path('<int:kit_id>', view=views.KitDetail.as_view(), name='kit'),
    path('<int:kit_id>/control', view=views.ControlKit.as_view(), name='control-kit'),
]
