"""Accounts Admin"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, VoterProfile, OTPRecord, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_email_verified')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')}),
    )


@admin.register(VoterProfile)
class VoterProfileAdmin(admin.ModelAdmin):
    list_display = ['voter_id', 'user', 'constituency', 'has_voted', 'is_eligible']
    list_filter = ['has_voted', 'is_eligible']
    search_fields = ['voter_id', 'user__email']


@admin.register(OTPRecord)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'purpose', 'is_used', 'created_at', 'expires_at']
    list_filter = ['purpose', 'is_used']
    readonly_fields = ['otp_code', 'created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'action', 'user', 'ip_address']
    list_filter = ['action']
    search_fields = ['user__email', 'ip_address', 'description']
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
