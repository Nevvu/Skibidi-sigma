# from django.test import TestCase
# from .models import *

# class CandidateModelTest(TestCase):
#     def setUp(self):
#         self.candidate = Candidate.objects.create(name="Juan Done")

#     def test_candidate_creation(self):
#         self.assertEqual(self.candidate.name, "Juan Done")

# class VoterModelTest(TestCase):
#     def setUp(self):
#         self.voter = Voter.objects.create(name="Harky Dog", pesel_num = '09227873143',eligible=True)

#     def test_voter_creation(self):
#         self.assertEqual(self.voter.name, "Harky Dog")
#         self.assertEqual(self.voter.pesel_num, '09227873143')
#         self.assertTrue(self.voter.eligible)

# class ElectionModelTest(TestCase):
#     def setUp(self):
#         self.election = Election.objects.create(title="Presidential Election 2024")

#     def test_election_creation(self):
#         self.assertEqual(self.election.title, "Presidential Election 2024")


from django.test import TestCase
from django.contrib.auth.models import User
from wybory.models import Voter, Notification
from wybory.utils import create_notification
from django.db.models.signals import post_save
from wybory.models import Voter, create_voter

class NotificationTests(TestCase):
    def setUp(self):
        post_save.disconnect(create_voter, sender=User)

        User.objects.all().delete()
        Voter.objects.all().delete()

        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.voter = Voter.objects.create(user=self.user, name='Test Voter', email='testuser@example.com')

    def tearDown(self):
        post_save.connect(create_voter, sender=User)

    def test_create_notification(self):
        title = "Test Notification"
        message = "This is a test notification."
        create_notification(self.user, title, message)

        notification = Notification.objects.filter(user=self.user).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.title, title)
        self.assertEqual(notification.message, message)

    def test_approve_verification_creates_notification(self):
        self.voter.verification_status = 'pending'
        self.voter.eligible = False
        self.voter.save()

        title = "Twoja weryfikacja została zatwierdzona"
        message = "Twoja weryfikacja została pomyślnie zatwierdzona. Możesz teraz brać udział w głosowaniach."
        create_notification(self.voter.user, title, message)
        
        notification = Notification.objects.filter(user=self.voter.user).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.title, title)
        self.assertEqual(notification.message, message)