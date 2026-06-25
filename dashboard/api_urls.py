"""API URL Configuration"""

from django.urls import path
from .views import TurnoutAPIView

app_name = 'api'

urlpatterns = [
    path('turnout/', TurnoutAPIView.as_view(), name='turnout'),
    path('turnout/<int:election_id>/', TurnoutAPIView.as_view(), name='turnout_detail'),
]
