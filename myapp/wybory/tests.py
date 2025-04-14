from django.test import TestCase
from .models import *

class CandidateModelTest(TestCase):
    def setUp(self):
        self.candidate = Candidate.objects.create(name="Juan Done")

    def test_candidate_creation(self):
        self.assertEqual(self.candidate.name, "Juan Done")

class VoterModelTest(TestCase):
    def setUp(self):
        self.voter = Voter.objects.create(name="Harky Dog", pesel_num = '09227873143',eligible=True)

    def test_voter_creation(self):
        self.assertEqual(self.voter.name, "Harky Dog")
        self.assertEqual(self.voter.pesel_num, '09227873143')
        self.assertTrue(self.voter.eligible)

class ElectionModelTest(TestCase):
    def setUp(self):
        self.election = Election.objects.create(title="Presidential Election 2024")

    def test_election_creation(self):
        self.assertEqual(self.election.title, "Presidential Election 2024")