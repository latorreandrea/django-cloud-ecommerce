from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ShirtigoOrder

@login_required
def order_list(request):
    """
    Simple view to display the user's Shirtigo orders.
    """
    # Retrieve the current user's orders
    orders = ShirtigoOrder.objects.filter(
        order__user=request.user
    ).order_by('-created_at')

    # Prepare the context to pass to the template
    context = {
        'orders': orders,
        'title': 'Your Orders',
    }

    # Render the template with the context
    return render(request, 'shirtigo/order_list.html', context)