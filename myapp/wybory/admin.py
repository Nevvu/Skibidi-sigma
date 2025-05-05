from django.contrib import admin
from .models import *
from django.urls import reverse
from django.utils.html import format_html

class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'end_time', 'generate_pdf')

    def generate_pdf(self, obj):
        url = reverse('election_summary_pdf', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Generuj PDF</a>', url)
    generate_pdf.short_description = 'Podsumowanie PDF'



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

class VoteAdmin(admin.ModelAdmin):
    list_display = ('election', 'candidate', 'timestamp')  
    readonly_fields = ('election', 'candidate', 'timestamp')  
    exclude = ('voter',)  

admin.site.register(Election, ElectionAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Voter, VoterAdmin)
admin.site.register(Candidate)
admin.site.register(VotingCriteria)
admin.site.register(ElectionType)
admin.site.register(Party)