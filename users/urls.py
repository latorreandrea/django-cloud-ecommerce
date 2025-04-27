from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.accounts, name='user_profile'),
    # path('orderhistory/', views.order_history, name='orderhistory'),
]