from django.views.generic import ListView, DetailView
from .models import Product
from django.shortcuts import render

# Create your views here.
class ProductListView(ListView):
    """
    View to list all products with pagination and search functionality.
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12  # Number of products per page

    def get_queryset(self):
        queryset = Product.objects.all()
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        if query:
            queryset = queryset.filter(name__icontains=query)
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        return queryset


class ProductDetailView(DetailView):
    """
    View to display the details of a single product.
    It includes related images and colors.
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'