"""
Votes Views
Handles: ballot display, vote submission, thank-you receipt page.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

from elections.models import Election
from candidates.models import Candidate
from votes.models import Vote


class BallotView(LoginRequiredMixin, View):
    template_name = 'votes/ballot.html'

    def get(self, request, election_id):
        election = get_object_or_404(Election, id=election_id)

        if not request.user.is_voter:
            messages.error(request, 'Only voters can access the ballot.')
            return redirect('dashboard:home')

        if not election.is_active:
            messages.error(request, 'This election is not currently active.')
            return redirect('dashboard:home')

        if Vote.objects.filter(voter=request.user, election=election).exists():
            messages.warning(request, 'You have already cast your vote.')
            return redirect('votes:thank_you', election_id=election_id)

        candidates = election.candidates.filter(is_active=True).order_by('display_order')
        return render(request, self.template_name, {'election': election, 'candidates': candidates})


class CastVoteView(LoginRequiredMixin, View):
    @method_decorator(csrf_protect)
    def post(self, request, election_id):
        election = get_object_or_404(Election, id=election_id)

        if not request.user.is_voter:
            return JsonResponse({'success': False, 'error': 'Access denied.'}, status=403)
        if not election.is_active:
            return JsonResponse({'success': False, 'error': 'Election is not active.'}, status=400)

        candidate_id = request.POST.get('candidate_id')
        if not candidate_id:
            return JsonResponse({'success': False, 'error': 'No candidate selected.'}, status=400)

        candidate = get_object_or_404(Candidate, id=candidate_id, election=election, is_active=True)

        try:
            vote = Vote.cast(voter=request.user, election=election, candidate=candidate, request=request)
            return JsonResponse({
                'success': True,
                'transaction_hash': vote.transaction_hash,
                'redirect': f'/votes/thank-you/{election_id}/?tx={vote.transaction_hash}'
            })
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class ThankYouView(LoginRequiredMixin, View):
    template_name = 'votes/thank_you.html'

    def get(self, request, election_id):
        election = get_object_or_404(Election, id=election_id)
        vote = Vote.objects.filter(voter=request.user, election=election).first()

        if not vote:
            return redirect('dashboard:home')

        return render(request, self.template_name, {
            'election': election, 'vote': vote, 'transaction_hash': vote.transaction_hash,
        })
