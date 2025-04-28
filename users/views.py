from django.shortcuts import render, get_object_or_404
from .models import UserProfile
# from checkout.models import Order
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def accounts(request):
    """ A view to show to the user the order history and manage his account"""
    account = get_object_or_404(UserProfile, user=request.user)
    
    context = {
        'account': account
    }   
    return render(request, 'accounts/accounts.html', context)