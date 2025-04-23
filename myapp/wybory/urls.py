from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='wybory/public/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('candidates/<int:election_id>/', views.candidate_list, name='candidate_list'),
    path('candidates/', views.candidate_search, name='candidate_search'),
    path('parties/', views.parties, name='parties'),
    path('results/', views.results, name='results'),
]
