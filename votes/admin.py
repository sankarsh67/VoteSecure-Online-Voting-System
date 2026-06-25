from django.contrib import admin
from .models import Vote

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['transaction_hash', 'election', 'cast_at']
    readonly_fields = [f.name for f in Vote._meta.fields]
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
