from django.urls import path
from . import views
from .webhook import stripe_webhook # Import the webhook function

urlpatterns = [
    path('', views.CheckoutView.as_view(), name='checkout'),
    path('create-order/', views.create_order, name='create_order'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    path('success/', views.CheckoutSuccessView.as_view(), name='checkout_success'),
]