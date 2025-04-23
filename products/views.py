from django.views.generic import ListView
from .models import Product
from django.shortcuts import render

# Create your views here.
class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12  # Number of products per page

    def get_queryset(self):
        return Product.objects.all()

