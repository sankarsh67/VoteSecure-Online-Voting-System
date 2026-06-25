from django.contrib import admin
from .models import Candidate

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'party_name', 'election', 'is_active', 'vote_count']
    list_filter = ['is_active', 'election']
    search_fields = ['name', 'party_name']
