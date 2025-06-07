import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from products.services import pipeline  

logger = logging.getLogger(__name__)

@staff_member_required
def update_products(request):
    """
    Protected view to update products from Shirtigo.
    """
    if request.method == 'POST':
        try:
            # Execute pipeline
            pipeline.main()
            messages.success(request, "product updated successfully")
            return redirect('admin:products_product_changelist')
        except Exception as e:
            logger.error(f"Error updating products: {str(e)}")
            messages.error(request, f"Error updating products: {str(e)}")
            return redirect('admin:products_product_changelist')
    else:
        # GET request shows the confirmation page
        return render(request, 'admin/products/update_confirmation.html')