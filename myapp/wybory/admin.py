from django.contrib import admin
from .models import *

admin.site.register(Candidate)
admin.site.register(Voter)
admin.site.register(Election)
admin.site.register(VotingCriteria)