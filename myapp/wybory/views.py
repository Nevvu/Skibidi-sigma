from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages  
from .models import *
from .forms import *
import datetime
from .forms import CustomUserCreationForm, CastVoteForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count
from weasyprint import HTML
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Notification
from wybory.utils import send_notification_email
from wybory.utils import create_notification





# --- Public views ---
def home(request):
    elections = Election.objects.all()
    return render(request, 'wybory/public/home.html', {'elections': elections})

def signup(request):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()  
        return redirect('login')
    return render(request, 'wybory/public/signup.html', {'form': form})

def faq(request): return render(request, 'wybory/public/faq.html')
def contact(request): return render(request, 'wybory/public/contact.html')
def results(request): return render(request, 'wybory/public/results.html')

def election_list(request):
    elections = Election.objects.all()
    return render(request, 'wybory/public/election_list.html', {'elections': elections})

def election_calendar(request):
    elections = Election.objects.filter(date__gte=datetime.date.today()).order_by('date')
    return render(request, 'wybory/public/election_calendar.html', {'elections': elections})

def parties(request):
    parties = Party.objects.all()
    return render(request, 'wybory/public/parties.html', {'parties': parties})

def candidate_list(request, election_id):
    candidates = Candidate.objects.filter(election_id=election_id)
    return render(request, 'wybory/public/candidate-list.html', {'candidates': candidates})

def candidate_search(request):
    selected_election_id = request.GET.get('election_id')
    candidates = Candidate.objects.filter(election_id=selected_election_id) if selected_election_id else None
    elections = Election.objects.all()
    return render(request, 'wybory/public/candidate-list.html', {
        'elections': elections, 'candidates': candidates, 'selected_election_id': selected_election_id
    })


def election_results(request):
    completed_elections = Election.objects.filter(end_time__lte=datetime.datetime.now())

    results = []
    for election in completed_elections:
        votes = Vote.objects.filter(election=election).values('candidate__name').annotate(vote_count=Count('id')).order_by('-vote_count')
        winner = votes.first() if votes else None
        results.append({
            'election': election,
            'winner': winner['candidate__name'] if winner else "Brak głosów",
            'votes': votes,
        })

    return render(request, 'wybory/public/results.html', {'results': results})

# --- Voting process ---


def election_detail(request, election_id):
    election = Election.objects.get(id=election_id)
    candidates = election.candidates.all()
    return render(request, 'wybory/voter/election_detail.html', {'election': election, 'candidates': candidates})

@login_required
def cast_vote(request, election_id):
    election = Election.objects.filter(id=election_id, date__gte=datetime.date.today()).first()
    if not election:
        messages.error(request, "Nie znaleziono wyborów lub są one niedostępne.")
        return redirect('voter_panel')

    if request.session.get(f'voted_{election_id}', False):
        messages.error(request, "Już oddałeś głos w tych wyborach.")
        return redirect('voter_panel')

    if request.method == 'POST':
        form = CastVoteForm(request.POST, election=election)
        if form.is_valid():
            candidate = form.cleaned_data['candidate']
            Vote.objects.create(candidate=candidate, election=election)

            request.session[f'voted_{election_id}'] = True

            messages.success(request, "Twój głos został oddany pomyślnie.")
            return redirect('voter_panel')
    else:
        form = CastVoteForm(election=election)

    return render(request, 'wybory/voter/cast_vote.html', {'election': election, 'form': form})
# --- Voter-only views ---
@login_required
def voter_panel(request): return render(request, 'wybory/voter/panel.html')

@login_required
def ballot(request):
    elections = Election.objects.filter(date__gte=datetime.date.today())
    voted_elections = [
        election_id for election_id in elections.values_list('id', flat=True)
        if request.session.get(f'voted_{election_id}', False)
    ]

    return render(request, 'wybory/voter/ballot.html', {
        'elections': elections,
        'voted_elections': voted_elections,
    })


@login_required
def activity_history(request):
    voter = Voter.objects.filter(user=request.user).first()
    if not voter:
        messages.error(request, "Nie znaleziono Twoich danych wyborcy.")
        return redirect('voter_panel')  

    votes = Vote.objects.filter(voter=voter).select_related('candidate', 'election')
    return render(request, 'wybory/voter/activity_history.html', {'votes': votes})


@login_required
def profile(request):
    voter = Voter.objects.filter(user=request.user).first()  
    if not voter:
        return redirect('verify_identity')  

    form = EditProfileForm(request.POST or None, instance=voter)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('profile')  

    return render(request, 'wybory/voter/profile.html', {'user': request.user, 'voter': voter, 'form': form})

@login_required
def verify_identity(request):
    voter = Voter.objects.filter(user=request.user).first()
    if not voter:
        voter = Voter.objects.create(user=request.user, name=request.user.username, email=request.user.email)

    form = VerificationForm(request.POST or None, instance=voter)
    if request.method == 'POST' and form.is_valid():
        form.save()
        voter.verification_status = 'pending'  
        voter.save()
        messages.success(request, "Twoje dane zostały przesłane do weryfikacji.")
        send_notification_email("Weryfikacja wyborcy", f"Witaj {voter.name},\n\nTwoje dane zostały przesłane do weryfikacji.", [voter.email])
        title = "Weryfikacja wyborcy"
        message = "Twoje dane zostały przesłane do weryfikacji. Oczekuj na dalsze instrukcje."
        create_notification(request.user, title, message)
        return redirect('voter_panel')  

    return render(request, 'wybory/voter/verify_identity.html', {'form': form})


@login_required
def generate_election_summary_pdf(request, election_id):
    election = Election.objects.get(id=election_id)
    candidates = Candidate.objects.filter(election=election)
    votes = Vote.objects.filter(election=election)

    candidate_support = []
    total_votes = votes.count()
    for candidate in candidates:
        candidate_votes = votes.filter(candidate=candidate).count()
        support_percentage = (candidate_votes / total_votes * 100) if total_votes > 0 else 0
        candidate_support.append({
            'name': candidate.name,
            'party': candidate.party.name if candidate.party else "Bezpartyjny",
            'votes': candidate_votes,
            'support_percentage': round(support_percentage, 2),
        })

    context = {
        'election': election,
        'candidates': candidate_support,
        'start_time': election.date,
        'end_time': election.end_time,
        'total_candidates': candidates.count(),
        'total_votes': total_votes,
    }

    html_string = render_to_string('wybory/pdf/election_summary.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())

    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="podsumowanie_wyborow_{election_id}.pdf"'
    return response






@login_required
def notifications(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        print(f"Received notification_id: {notification_id}")  
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        print(f"Notification found: {notification}")  
        if not notification.is_read:
            notification.is_read = True
            notification.save()
            print(f"Notification {notification_id} marked as read")  
        return JsonResponse({'status': 'success', 'message': 'Powiadomienie oznaczone jako przeczytane'})

    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'wybory/voter/notifications.html', {'notifications': user_notifications})