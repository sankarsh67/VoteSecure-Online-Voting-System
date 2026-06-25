"""Accounts URL Configuration"""

from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='accounts:login')),
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-otp/', views.OTPVerificationView.as_view(), name='verify_otp'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.VoterRegisterView.as_view(), name='register_voter'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('upload-voters/', views.VoterCSVUploadView.as_view(), name='upload_voters'),
]
