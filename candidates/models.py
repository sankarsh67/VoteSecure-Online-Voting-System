"""
Candidates Models
Defines Candidate with photo, party symbol, and election association.
"""

from django.db import models


class Candidate(models.Model):
    election = models.ForeignKey(
        'elections.Election',
        on_delete=models.CASCADE,
        related_name='candidates'
    )
    name = models.CharField(max_length=150)
    party_name = models.CharField(max_length=150, blank=True)
    party_symbol = models.ImageField(
        upload_to='candidates/symbols/', null=True, blank=True,
        help_text='Party symbol image (PNG/SVG recommended)'
    )
    photo = models.ImageField(upload_to='candidates/photos/', null=True, blank=True)
    bio = models.TextField(blank=True, help_text='Short biography shown on ballot')
    manifesto_points = models.TextField(blank=True, help_text='Key manifesto points (one per line)')
    display_order = models.PositiveIntegerField(default=0, help_text='Order on ballot page')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'candidates'
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.party_name}) — {self.election}"

    @property
    def vote_count(self):
        return self.votes.count()

    @property
    def manifesto_list(self):
        return [p.strip() for p in self.manifesto_points.split('\n') if p.strip()]

    @property
    def photo_url(self):
        if self.photo:
            return self.photo.url
        return '/static/images/default_candidate.png'

    @property
    def symbol_url(self):
        if self.party_symbol:
            return self.party_symbol.url
        return '/static/images/default_symbol.png'
