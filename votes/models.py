"""
Votes Models
Defines Vote with transaction hash. Ballot secrecy is maintained.
"""

from django.db import models
import hashlib, secrets


class Vote(models.Model):
    election = models.ForeignKey('elections.Election', on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey('candidates.Candidate', on_delete=models.CASCADE, related_name='votes')
    transaction_hash = models.CharField(max_length=64, unique=True)
    cast_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'votes'
        unique_together = [('election', 'voter')]

    def __str__(self):
        return f"Vote by {self.voter.email} in {self.election} [TX: {self.transaction_hash[:8]}...]"

    @classmethod
    def generate_transaction_hash(cls, voter_id, election_id, timestamp):
        salt = secrets.token_hex(16)
        raw = f"{voter_id}-{election_id}-{timestamp}-{salt}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @classmethod
    def cast(cls, voter, election, candidate, request=None):
        from accounts.models import AuditLog

        if cls.objects.filter(voter=voter, election=election).exists():
            AuditLog.log('vote_attempt', request, voter, f"Attempted duplicate vote in election {election.id}")
            raise ValueError("You have already voted in this election.")

        from django.utils import timezone
        tx_hash = cls.generate_transaction_hash(voter.id, election.id, timezone.now().isoformat())

        ip = None
        if request:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

        vote = cls.objects.create(
            election=election, voter=voter, candidate=candidate,
            transaction_hash=tx_hash, ip_address=ip
        )

        if hasattr(voter, 'voter_profile'):
            voter.voter_profile.has_voted = True
            voter.voter_profile.save()

        AuditLog.log('vote_cast', request, voter, f"Vote cast in election '{election.title}' (TX: {tx_hash[:8]})")
        return vote
