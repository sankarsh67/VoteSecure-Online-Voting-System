"""
Elections Models
Defines Election configuration with dates, rules, and active status.
Includes auto-close fix: status updates to 'closed' on save if end time has passed.
"""

from django.db import models
from django.utils import timezone


class Election(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('results', 'Results Published'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True, help_text='Voting rules shown to voters')

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    results_published = models.BooleanField(default=False)
    results_published_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_elections'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'elections'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        """Returns True if election is currently within voting window."""
        now = timezone.now()
        return self.status == 'active' and self.start_datetime <= now <= self.end_datetime

    def save(self, *args, **kwargs):
        """Auto-update status to 'closed' if end time has passed."""
        now = timezone.now()
        if self.status == 'active' and self.end_datetime and now > self.end_datetime:
            self.status = 'closed'
        super().save(*args, **kwargs)

    @property
    def has_started(self):
        return timezone.now() >= self.start_datetime

    @property
    def has_ended(self):
        return timezone.now() > self.end_datetime

    @property
    def total_votes(self):
        return self.votes.count()

    def publish_results(self):
        self.results_published = True
        self.results_published_at = timezone.now()
        self.status = 'results'
        self.save()
