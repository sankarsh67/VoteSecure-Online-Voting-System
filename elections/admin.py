from django.contrib import admin
from .models import Election

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'start_datetime', 'end_datetime', 'total_votes']
    list_filter = ['status']
    search_fields = ['title']
