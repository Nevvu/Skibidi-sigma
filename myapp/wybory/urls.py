from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='wybory/public/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('candidates/', views.candidate_search, name='candidate_search'),
    path('parties/', views.parties, name='parties'),
    path('results/', views.results, name='results'),
    path('elections/', views.election_list, name='election_list'),
    path('elections/<int:election_id>/', views.election_detail, name='election_detail'),
    path('candidates/<int:election_id>/', views.candidate_list, name='candidate_list'),
    path('calendar/', views.election_calendar, name='election_calendar'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('voter/panel/', views.voter_panel, name='voter_panel'),
    path('voter/ballot/', views.ballot, name='ballot'),
    path('voter/history/', views.activity_history, name='activity_history'),
    path('voter/profile/', views.profile, name='profile'),
    path('voter/verify/', views.verify_identity, name='verify_identity'),
]
from django.urls import path
from . import views

