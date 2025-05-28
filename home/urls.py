from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('our-mission/', views.our_mission, name='our_mission'),
    path('contact/', views.contact, name='contact'),
    path('support/', views.support, name='support'),
    path('faq/', views.faq, name='faq'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
]
