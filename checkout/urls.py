from django.urls import path
from . import views

urlpatterns = [
    path('', views.CheckoutView.as_view(), name='checkout'),
    path('success/', views.success, name='checkout_success'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]