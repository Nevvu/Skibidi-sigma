from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
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
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.core.mail import EmailMultiAlternatives
from .forms import CustomUserCreationForm as SignUpForm
from .utils import account_activation_token
from django.shortcuts import render

from django.contrib.auth import login
import requests
from django.conf import settings

import matplotlib.pyplot as plt
import io
import base64

from .models import Voter
from .forms import PartyVoteForm

import logging

logger = logging.getLogger('myapp')

def my_view(request):
    logger.info("To jest log informacyjny")
    logger.error("Coś poszło nie tak!")


def index(request):
    logger.info("Strona główna została odwiedzona")
    return render(request, 'signup.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        # Sprawdzenie reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': '6LdREUkrAAAAAGxiNBHatbkyMG8vOY_KpwoP6_Tq',  # NIE PUBLICZNY
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if form.is_valid() and result.get('success'):
            form.save()
            return redirect('login')  # lub inna strona po rejestracji
        else:
            messages.error(request, 'Błąd rejestracji lub nieprawidłowa CAPTCHA.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Aktywuj swoje konto'
            message = render_to_string('wybory/emails/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            send_notification_email(subject, message, [user.email])
            messages.success(request, 'Rejestracja zakończona! Sprawdź e-mail, aby aktywować konto.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'wybory/public/signup.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # Dodajemy Voter tylko jeśli nie istnieje
        if not hasattr(user, 'voter'):
            Voter.objects.create(user=user, name=user.username, email=user.email)

        login(request, user)
        messages.success(request, 'Konto zostało aktywowane!')
        return redirect('home')
    else:
        return HttpResponse('Link aktywacyjny jest nieprawidłowy lub wygasł.')
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Konto nieaktywne. Sprawdź e-mail.')
        else:
            messages.error(request, 'Nieprawidłowy login lub hasło.')
    return render(request, 'wybory/public/login.html')



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
            return redirect('ballot')
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
    party_voted_elections = [
        election_id for election_id in elections.values_list('id', flat=True)
        if request.session.get(f'party_voted_{election_id}', False)
    ]

    presidential_elections = elections.filter(election_type__name="Prezydenckie")
    parliamentary_elections = elections.filter(election_type__name="Parlamentarne")

    return render(request, 'wybory/voter/ballot.html', {
        'presidential_elections': presidential_elections,
        'parliamentary_elections': parliamentary_elections,
        'voted_elections': voted_elections,
        'party_voted_elections': party_voted_elections,
    })

@login_required
def activity_history(request):
    voted_elections_ids = [
        int(key.split('_')[1]) for key in request.session.keys() if key.startswith('voted_') and request.session[key]
    ]
    voted_elections = Election.objects.filter(id__in=voted_elections_ids)

    return render(request, 'wybory/voter/activity_history.html', {'voted_elections': voted_elections})


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


# @login_required
# def generate_election_summary_pdf(request, election_id):
#     election = Election.objects.get(id=election_id)
#     candidates = Candidate.objects.filter(election=election)
#     votes = Vote.objects.filter(election=election)

#     candidate_support = []
#     total_votes = votes.count()
#     for candidate in candidates:
#         candidate_votes = votes.filter(candidate=candidate).count()
#         support_percentage = (candidate_votes / total_votes * 100) if total_votes > 0 else 0
#         candidate_support.append({
#             'name': candidate.name,
#             'party': candidate.party.name if candidate.party else "Bezpartyjny",
#             'votes': candidate_votes,
#             'support_percentage': round(support_percentage, 2),
#         })

#     context = {
#         'election': election,
#         'candidates': candidate_support,
#         'start_time': election.date,
#         'end_time': election.end_time,
#         'total_candidates': candidates.count(),
#         'total_votes': total_votes,
#     }

#     html_string = render_to_string('wybory/pdf/election_summary.html', context)
#     html = HTML(string=html_string, base_url=request.build_absolute_uri())

#     pdf_file = html.write_pdf()

#     response = HttpResponse(pdf_file, content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="podsumowanie_wyborow_{election_id}.pdf"'
#     return response


# @login_required
def generate_election_summary_pdf(request, election_id):
    election = Election.objects.get(id=election_id)
    candidates = Candidate.objects.filter(election=election)
    votes = Vote.objects.filter(election=election)

    candidate_support = []
    total_votes = votes.count()
    candidate_names = []
    candidate_votes_list = []

    for candidate in candidates:
        candidate_votes = votes.filter(candidate=candidate).count()
        support_percentage = (candidate_votes / total_votes * 100) if total_votes > 0 else 0
        candidate_support.append({
            'name': candidate.name,
            'party': candidate.party.name if candidate.party else "Bezpartyjny",
            'votes': candidate_votes,
            'support_percentage': round(support_percentage, 2),
        })
        candidate_names.append(candidate.name)
        candidate_votes_list.append(candidate_votes)

    # Generowanie wykresu
    plt.figure(figsize=(6, 6))
    plt.pie(candidate_votes_list, labels=candidate_names, autopct='%1.1f%%', startangle=140)
    plt.title(f"Wyniki wyborów: {election.title}")

    # Zapisanie wykresu do pamięci jako obraz
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    # Kontekst dla szablonu
    context = {
        'election': election,
        'candidates': candidate_support,
        'start_time': election.date,
        'end_time': election.end_time,
        'total_candidates': candidates.count(),
        'total_votes': total_votes,
        'chart': image_base64,  # Wykres w formacie base64
    }

    # Renderowanie szablonu HTML
    html_string = render_to_string('wybory/pdf/election_summary.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())

    # Generowanie pliku PDF
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

from django.contrib.auth.decorators import user_passes_test

# --- Moderator-only views ---
def is_moderator(user):
    return user.groups.filter(name='Moderator').exists()

@login_required
@user_passes_test(is_moderator)
def verify_voters(request):
    voters = Voter.objects.filter(verification_status='pending')

    if request.method == 'POST':
        voter_id = request.POST.get('voter_id')
        action = request.POST.get('action')  # 'approve' lub 'reject'
        voter = get_object_or_404(Voter, id=voter_id)

        if action == 'approve':
            voter.verification_status = 'approved'
            voter.save()
            messages.success(request, f"Użytkownik {voter.name} został zatwierdzony.")
        elif action == 'reject':
            voter.verification_status = 'rejected'
            voter.save()
            messages.success(request, f"Użytkownik {voter.name} został odrzucony.")

        return redirect('verify_voters')

    return render(request, 'wybory/moderator/verify_voters.html', {'voters': voters})


def home(request):
    presidential_elections = Election.objects.filter(election_type__name="Prezydenckie")
    parliamentary_elections = Election.objects.filter(election_type__name="Parlamentarne")

    return render(request, 'wybory/public/home.html', {
        'presidential_elections': presidential_elections,
        'parliamentary_elections': parliamentary_elections,
    })

@login_required
def cast_party_vote(request, election_id):
    election = Election.objects.filter(id=election_id, date__gte=datetime.date.today()).first()
    if not election:
        messages.error(request, "Nie znaleziono wyborów lub są one niedostępne.")
        return redirect('voter_panel')

    if request.session.get(f'party_voted_{election_id}', False):
        messages.error(request, "Już oddałeś głos na partię w tych wyborach.")
        return redirect('voter_panel')

    if request.method == 'POST':
        form = PartyVoteForm(request.POST, election=election)
        if form.is_valid():
            party = form.cleaned_data['party']
            PartyVote.objects.create(party=party, election=election)
            request.session[f'party_voted_{election_id}'] = True
            messages.success(request, "Twój głos na partię został oddany pomyślnie.")
            return redirect('ballot')
    else:
        form = PartyVoteForm(election=election)

    # Przekazanie formularza i wyborów do szablonu
    return render(request, 'wybory/voter/cast_party_vote.html', {
        'election': election,
        'form': form,
    })

@login_required
def party_vote_results(request, election_id):
    election = Election.objects.get(id=election_id)
    party_votes = PartyVote.objects.filter(election=election).values('party__name').annotate(total_votes=Count('id')).order_by('-total_votes')

    return render(request, 'wybory/voter/party_vote_results.html', {'election': election, 'party_votes': party_votes})