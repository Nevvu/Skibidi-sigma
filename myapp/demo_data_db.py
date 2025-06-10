# seed_demo_data.py
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")
django.setup()

from django.contrib.auth.models import User
from wybory.models import (
    ElectionType, Election, Party, Candidate, Vote,
    PartyVote, VotingCriteria, ElectionResult
)

def seed():
    # Użytkownik + domyślny voter
    user2 = User.objects.create_user(username="andrzej_nowak", email="nowak@example.com", password="test1234")

   
    presidential = ElectionType.objects.create(name="Prezydenckie", description="Wybory prezydenckie 2025")

    # Wybory
    election = Election.objects.create(
        title="Wybory 2025",
        election_type=presidential,
        date=datetime.now(),
        end_time=datetime.now() + timedelta(days=1),
        description="Opis wyborów prezydenckich"
    )

    # Partie
    party1 = Party.objects.create(name="Partia ABC", description="Partia A - demo", election=election)
    party2 = Party.objects.create(name="Partia CBD", description="Partia B - demo", election=election)

    # Kandydaci
    cand1 = Candidate.objects.create(name="Kandydat Abc", election=election, party=party1)
    cand2 = Candidate.objects.create(name="Kandydat Bcd", election=election, party=party2)

    # Kryteria głosowania
    VotingCriteria.objects.create(election=election, age_min=18, age_max=120, residency_required=True)

    # Głosy
    Vote.objects.create(candidate=cand1, election=election)
    Vote.objects.create(candidate=cand2, election=election)
    PartyVote.objects.create(party=party1, election=election)

    # Wyniki
    ElectionResult.objects.create(election=election, candidate=cand1, votes_count=1)
    ElectionResult.objects.create(election=election, candidate=cand2, votes_count=1)

    print("Dane demo zostały załadowane.")

if __name__ == "__main__":
    seed()
