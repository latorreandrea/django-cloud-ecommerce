from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', views.subscribe_to_newsletter, name='subscribe'),
    path('unsubscribe/<str:token>/', views.unsubscribe_from_newsletter, name='unsubscribe'),
]