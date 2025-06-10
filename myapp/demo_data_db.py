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
    NUM_USERS = 500
    NUM_PARTIES = 10
    NUM_CANDIDATES = 10

    print(" Czyszczenie istniejących danych...")
    Vote.objects.all().delete()
    ElectionResult.objects.all().delete()
    Candidate.objects.all().delete()
    PartyVote.objects.all().delete()
    Party.objects.all().delete()
    VotingCriteria.objects.all().delete()
    Election.objects.all().delete()
    ElectionType.objects.all().delete()
    User.objects.filter(username__startswith="user_").delete()

    print(" Tworzenie typów wyborów...")
    prezydenckie = ElectionType(name="Prezydenckie", description="Wybory prezydenckie 2025")
    parlamentarne = ElectionType(name="Parlamentarne", description="Wybory parlamentarne 2025")
    prezydenckie.save()
    parlamentarne.save()

    print(" Tworzenie wyborów...")
    prezydent_election = Election(
        title="Wybory Prezydenckie 2025",
        election_type=prezydenckie,
        date=datetime.now(),
        end_time=datetime.now() + timedelta(days=1),
        description="Wybory prezydenckie"
    )
    prezydent_election.save()

    parlament_election = Election(
        title="Wybory Parlamentarne 2025",
        election_type=parlamentarne,
        date=datetime.now(),
        end_time=datetime.now() + timedelta(days=1),
        description="Wybory parlamentarne"
    )
    parlament_election.save()

    print(" Tworzenie partii...")
    parties = []
    for i in range(NUM_PARTIES):
        partia = Party(
            name=f"Partia_{i}",
            description=f"Partia demo {i}",
            election=prezydent_election if i < 5 else parlament_election
        )
        partia.save()
        parties.append(partia)

    print(" Tworzenie kandydatów...")
    candidates = []
    for i in range(5):
        kand = Candidate(
            name=f"Kandydat_{i}",
            election=prezydent_election,
            party=parties[i]
        )
        kand.save()
        candidates.append(kand)

    for i in range(5):
        kand = Candidate(
            name=f"Kandydat_{i+5}",
            election=parlament_election,
            party=parties[5 + i]
        )
        kand.save()
        candidates.append(kand)

    print(" Dodawanie kryteriów głosowania...")
    vc1 = VotingCriteria(election=prezydent_election, age_min=18, age_max=120, residency_required=True)
    vc1.save()
    vc2 = VotingCriteria(election=parlament_election, age_min=18, age_max=120, residency_required=True)
    vc2.save()

    print("Tworzenie 100 000 użytkowników...")
    for i in range(NUM_USERS):
        u = User(username=f"usertest_{i}", email=f"user_{i}@example.com")
        u.set_password("test1234")
        u.save()
        if i % 10000 == 0:
            print(f"  → {i} użytkowników stworzonych")

    print("Tworzenie głosów...")
    for i in range(500):
        v1 = Vote(candidate=candidates[0], election=prezydent_election)
        v1.save()
        v2 = Vote(candidate=candidates[1], election=prezydent_election)
        v2.save()
        if i % 10000 == 0:
            print(f"  → {i*2} głosów prezydenckich dodanych")

    for i in range(50_000):
        v1 = Vote(candidate=candidates[5], election=parlament_election)
        v1.save()
        v2 = Vote(candidate=candidates[6], election=parlament_election)
        v2.save()
        if i % 10000 == 0:
            print(f"  → {i*2} głosów parlamentarnych dodanych")

    print(" Dodawanie wyników wyborów...")
    er1 = ElectionResult(election=prezydent_election, candidate=candidates[0], votes_count=50000)
    er1.save()
    er2 = ElectionResult(election=prezydent_election, candidate=candidates[1], votes_count=50000)
    er2.save()
    er3 = ElectionResult(election=parlament_election, candidate=candidates[5], votes_count=50000)
    er3.save()
    er4 = ElectionResult(election=parlament_election, candidate=candidates[6], votes_count=50000)
    er4.save()

    print("🏷️ Tworzenie party votes...")
    PartyVote(party=parties[0], election=prezydent_election).save()
    PartyVote(party=parties[5], election=parlament_election).save()

    print(" Załadowano dane demo do bazy!")

if __name__ == "__main__":
    seed()
