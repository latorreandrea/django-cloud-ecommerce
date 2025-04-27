from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.accounts, name='accounts'),
    # path('orderhistory/', views.order_history, name='orderhistory'),
]