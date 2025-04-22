from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth import logout


def home(request):
    elections = Election.objects.all()
    return render(request, 'wybory/home.html', {'elections': elections})

def candidate_list(request, election_id):
    candidates = Candidate.objects.filter(election_id=election_id)
    return render(request, 'wybory/lista-kandydatow.html', {'candidates': candidates})

def eligible_voters(request, election_id):
    voters = Voter.objects.filter(election_id=election_id, eligible=True)
    return render(request, 'wybory/uprawnieni_wyborcy.html', {'voters': voters})

def cast_vote(request, election_id):
    if request.method == 'POST':
        voter_id = request.POST.get('voter_id')
        candidate_id = request.POST.get('candidate_id')
        if Voter.objects.filter(id=voter_id, eligible=True).exists():
            Vote.objects.create(voter_id=voter_id, candidate_id=candidate_id, election_id=election_id)
            return JsonResponse({'status': 'success', 'message': 'Vote cast successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Voter not eligible.'})
    return render(request, 'wybory/oddaj_glos.html', {'election_id': election_id})

def election_results(request, election_id):
    results = Vote.objects.filter(election_id=election_id).values('candidate_id').annotate(vote_count=models.Count('id'))
    return render(request, 'wybory/wyniki_wyborow.html', {'results': results})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'wybory/signup.html', {'form': form})


