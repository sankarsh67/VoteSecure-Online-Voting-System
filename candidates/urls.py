"""Candidates URL Configuration"""
from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    path('add/<int:election_id>/', views.AddCandidateView.as_view(), name='add'),
    path('edit/<int:candidate_id>/', views.EditCandidateView.as_view(), name='edit'),
]
