from django.db import models

# Create your models here.

# class Election(models.Model):
#     ELECTION_TYPES = [
#         ('presidential', 'Presidential'),
#         ('parliamentary', 'Parliamentary'),
#         ('starosty', 'Starosty'),
#         ('dean', 'Dean'),
#     ]

#     title = models.CharField(max_length = 100)
#     election_type = models.CharField(max_length = 20, choices=ELECTION_TYPES)
#     date = models.DateField()
#     description = models.TextField()

class ElectionType(models.Model):
    name = models.CharField(max_length=50, unique=True)  
    description = models.TextField(null=True, blank=True)  

    def __str__(self):
        return self.name


class Election(models.Model):
    title = models.CharField(max_length=100)
    election_type = models.ForeignKey(ElectionType, on_delete=models.CASCADE, related_name='elections')  
    date = models.DateField()
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
    name = models.CharField(max_length = 100)
    email = models.EmailField(unique=True)
    pesel_num = models.CharField(max_length = 11, unique=True)
    eligible = models.BooleanField(default=True)


class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete = models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete = models.CASCADE)
    election = models.ForeignKey(Election, on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add = True)    

class VotingCriteria(models.Model):
    election = models.OneToOneField(Election, on_delete=models.CASCADE)
    age_min = models.PositiveIntegerField()
    age_max = models.PositiveIntegerField()
    residency_required = models.BooleanField(default=True)

class ElectionResult(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    votes_count = models.PositiveIntegerField(default=0)