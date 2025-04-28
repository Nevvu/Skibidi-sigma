from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import *



def home(request):
    elections = Election.objects.all()
    return render(request, 'wybory/public/home.html', {'elections': elections})

def candidate_list(request, election_id):
    candidates = Candidate.objects.filter(election_id=election_id)
    return render(request, 'wybory/public/candidate-list.html', {'candidates': candidates})

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
    return render(request, 'wybory/voter/vote.html', {'election_id': election_id})

def election_results(request, election_id):
    results = Vote.objects.filter(election_id=election_id).values('candidate_id').annotate(vote_count=models.Count('id'))
    return render(request, 'wybory/public/wyniki_wyborow.html', {'results': results})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'wybory/public/signup.html', {'form': form})

def candidate_search(request):
    elections = Election.objects.all()
    selected_election_id = request.GET.get('election_id') 
    candidates = Candidate.objects.filter(election_id=selected_election_id) if selected_election_id else None

    return render(request, 'wybory/public/candidate-list.html', {
        'elections': elections,
        'candidates': candidates,
        'selected_election_id': selected_election_id,
    })

# def parties(request):
#     return render(request, 'wybory/public/parties.html')

# def party_list(request):
#     parties = Party.objects.all()
#     return render(request, 'wybory/party_list.html', {'parties': parties})

def parties(request):
    parties = Party.objects.all()
    return render(request, 'wybory/public/parties.html', {'parties': parties})

def results(request):
    return render(request, 'wybory/public/results.html')

def election_list(request):
    elections = Election.objects.all()
    return render(request, 'wybory/public/election_list.html', {'elections': elections})

def election_detail(request, election_id):
    election = Election.objects.get(id=election_id)
    candidates = election.candidates.all()
    return render(request, 'wybory/voter/election_detail.html', {'election': election, 'candidates': candidates})

def election_calendar(request):
    elections = Election.objects.all().order_by('date')
    return render(request, 'wybory/public/election_calendar.html', {'elections': elections})

def faq(request):
    return render(request, 'wybory/public/faq.html')

def contact(request):
    return render(request, 'wybory/public/contact.html')



@login_required
def voter_panel(request):
    return render(request, 'wybory/voter/panel.html')

@login_required
def ballot(request):
    voter = Voter.objects.filter(email=request.user.email).first()
    if not voter or not voter.eligible:
        return redirect('verify_identity')  

    elections = Election.objects.filter(date__gte=datetime.date.today())
    return render(request, 'wybory/voter/ballot.html', {'elections': elections})

@login_required
def activity_history(request):
    voter = Voter.objects.filter(email=request.user.email).first()  
    if not voter:
        return JsonResponse({'status': 'error', 'message': 'Nie znaleziono użytkownika w bazie wyborców.'})

    votes = Vote.objects.filter(voter=voter)  
    return render(request, 'wybory/voter/activity_history.html', {'votes': votes})


@login_required
def profile(request):
    voter = Voter.objects.filter(email=request.user.email).first()

    if not voter:
        return redirect('verify_identity') 

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=voter)
        if form.is_valid():
            form.save()
            return redirect('profile')  
    else:
        form = EditProfileForm(instance=voter)

    return render(request, 'wybory/voter/profile.html', {'user': request.user, 'voter': voter, 'form': form})

@login_required
def verify_identity(request):
    voter = Voter.objects.filter(email=request.user.email).first()

    if not voter:
        return JsonResponse({'status': 'error', 'message': 'Nie znaleziono użytkownika w bazie wyborców.'})

    if request.method == 'POST':
        form = VerificationForm(request.POST, instance=voter)
        if form.is_valid():
            form.save()
            voter.verification_status = 'pending'  
            voter.save()
            return redirect('voter_panel')  
    else:
        form = VerificationForm(instance=voter)

    return render(request, 'wybory/voter/verify_identity.html', {'form': form})