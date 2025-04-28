from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.UserProfileDetailView.as_view(), name='user_profile'),
    path('edit/', views.UserProfileUpdateView.as_view(), name='edit_profile'),
    # path('orderhistory/', views.order_history, name='orderhistory'),
]