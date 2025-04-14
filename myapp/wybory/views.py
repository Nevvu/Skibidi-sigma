from django.shortcuts import render
from django.http import JsonResponse
from .models import *

def home(request):
    return render(request, 'wybory/home.html')

def candidate_list(request, election_id):
    candidates = Candidate.objects.filter(election_id=election_id)
    return render(request, 'wybory/candidate_list.html', {'candidates': candidates})

def eligible_voters(request, election_id):
    voters = Voter.objects.filter(election_id=election_id, eligible=True)
    return render(request, 'wybory/eligible_voters.html', {'voters': voters})

def cast_vote(request, election_id):
    if request.method == 'POST':
        voter_id = request.POST.get('voter_id')
        candidate_id = request.POST.get('candidate_id')
        if Voter.objects.filter(id=voter_id, eligible=True).exists():
            Vote.objects.create(voter_id=voter_id, candidate_id=candidate_id, election_id=election_id)
            return JsonResponse({'status': 'success', 'message': 'Vote cast successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Voter not eligible.'})
    return render(request, 'wybory/cast_vote.html', {'election_id': election_id})

def election_results(request, election_id):
    results = Vote.objects.filter(election_id=election_id).values('candidate_id').annotate(vote_count=models.Count('id'))
    return render(request, 'wybory/election_results.html', {'results': results})