from django.contrib import admin
from .models import *

class VoterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'pesel_num', 'eligible', 'verification_status')
    list_filter = ('eligible', 'verification_status')  
    search_fields = ('name', 'email', 'pesel_num')  
    readonly_fields = ('email',)  
    actions = ['approve_verification', 'reject_verification'] 

    def approve_verification(self, request, queryset):
        for voter in queryset:
            voter.verification_status = 'approved'
            voter.eligible = True
            voter.save()
    approve_verification.short_description = 'Zatwierdź wybranych użytkowników'

    def reject_verification(self, request, queryset):
        for voter in queryset:
            voter.verification_status = 'rejected'
            voter.eligible = False
            voter.save()
    reject_verification.short_description = 'Odrzuć wybranych użytkowników'

admin.site.register(Voter, VoterAdmin)
admin.site.register(Candidate)
admin.site.register(Election)
admin.site.register(VotingCriteria)
admin.site.register(ElectionType)
admin.site.register(Party)