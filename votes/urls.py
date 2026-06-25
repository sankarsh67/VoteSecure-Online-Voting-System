"""Votes URL Configuration"""
from django.urls import path
from . import views

app_name = 'votes'

urlpatterns = [
    path('ballot/<int:election_id>/', views.BallotView.as_view(), name='ballot'),
    path('cast/<int:election_id>/', views.CastVoteView.as_view(), name='cast_vote'),
    path('thank-you/<int:election_id>/', views.ThankYouView.as_view(), name='thank_you'),
]
