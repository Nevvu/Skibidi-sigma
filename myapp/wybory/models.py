from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class ElectionType(models.Model):
    name = models.CharField(max_length=50, unique=True)  
    description = models.TextField(null=True, blank=True)  

    def __str__(self):
        return self.name


class Election(models.Model):
    title = models.CharField(max_length=100)
    election_type = models.ForeignKey(ElectionType, on_delete=models.CASCADE, related_name='elections')  
    date = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Party(models.Model):
    name = models.CharField(max_length=100, unique=True)  
    description = models.TextField(null=True, blank=True) 
    founded_date = models.DateField(null=True, blank=True) 

    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    election = models.ForeignKey(Election, related_name='candidates', on_delete=models.CASCADE)
    party = models.ForeignKey(Party, null=True, blank=True, on_delete=models.SET_NULL)  

    def __str__(self):
        return self.name




class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  
    last_name = models.CharField(max_length=100, blank=True, null=True)  
    email = models.EmailField(unique=True)
    pesel_num = models.CharField(max_length=11)
    eligible = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Oczekujące'), ('approved', 'Zatwierdzone'), ('rejected', 'Odrzucone')],
        default='pending'
    )

    def __str__(self):
        return f"{self.name} {self.last_name}"

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete = models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete = models.CASCADE)
    election = models.ForeignKey(Election, on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add = True)    

@receiver(post_save, sender=User)
def create_voter(sender, instance, created, **kwargs):
    if created:
        Voter.objects.create(user=instance, name=instance.username, email=instance.email)

class VotingCriteria(models.Model):
    election = models.OneToOneField(Election, on_delete=models.CASCADE)
    age_min = models.PositiveIntegerField()
    age_max = models.PositiveIntegerField()
    residency_required = models.BooleanField(default=True)

class ElectionResult(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    votes_count = models.PositiveIntegerField(default=0)