"""Dashboard URL Configuration"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('admin/', views.AdminDashboardView.as_view(), name='admin_home'),
    path('voter/', views.VoterDashboardView.as_view(), name='voter_home'),
    path('elections/configure/', views.ElectionConfigView.as_view(), name='election_configure'),
    path('elections/configure/<int:election_id>/', views.ElectionConfigView.as_view(), name='election_edit'),
    path('elections/results/<int:election_id>/', views.ElectionResultsView.as_view(), name='results'),
    path('export/results/<int:election_id>/', views.ExportResultsView.as_view(), name='export_results'),
    path('send-email/', views.SendEmailNotificationView.as_view(), name='send_email'),
]
