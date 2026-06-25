"""
Candidates Views
Admin: Add and edit candidates with photo + party symbol upload.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django import forms

from elections.models import Election
from candidates.models import Candidate
from accounts.models import AuditLog


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'party_name', 'photo', 'party_symbol', 'bio', 'manifesto_points', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'party_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manifesto_points': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'One point per line'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AddCandidateView(LoginRequiredMixin, View):
    template_name = 'candidates/form.html'

    def get(self, request, election_id):
        if not request.user.is_admin:
            return redirect('dashboard:home')
        election = get_object_or_404(Election, id=election_id)
        return render(request, self.template_name, {'form': CandidateForm(), 'election': election})

    def post(self, request, election_id):
        if not request.user.is_admin:
            return redirect('dashboard:home')
        election = get_object_or_404(Election, id=election_id)
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.election = election
            candidate.save()
            AuditLog.log('candidate_added', request, request.user, f'Added {candidate.name}')
            messages.success(request, f'{candidate.name} added successfully.')
            return redirect('dashboard:admin_home')
        return render(request, self.template_name, {'form': form, 'election': election})


class EditCandidateView(LoginRequiredMixin, View):
    template_name = 'candidates/form.html'

    def get(self, request, candidate_id):
        if not request.user.is_admin:
            return redirect('dashboard:home')
        candidate = get_object_or_404(Candidate, id=candidate_id)
        return render(request, self.template_name, {
            'form': CandidateForm(instance=candidate),
            'election': candidate.election, 'candidate': candidate,
        })

    def post(self, request, candidate_id):
        if not request.user.is_admin:
            return redirect('dashboard:home')
        candidate = get_object_or_404(Candidate, id=candidate_id)
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate updated.')
            return redirect('dashboard:admin_home')
        return render(request, self.template_name, {
            'form': form, 'election': candidate.election, 'candidate': candidate,
        })
