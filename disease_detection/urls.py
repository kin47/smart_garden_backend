from django.urls import path
from . import views

urlpatterns = [
    path('predict', view=views.DiseaseDetection.as_view(), name='predict'),
    path('history', view=views.HistoryPredictDisease.as_view(), name='history'),
]
