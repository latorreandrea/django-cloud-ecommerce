from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .models import Cart, CartItem

# Create your views here.
def view_cart(request):
    """
    View the cart.
    If the user is authenticated, use the Cart model.
    If the user is not authenticated, use the session to store cart items.
    """
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
    else:
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
        request.session['cart'] = cart

    return redirect('products_list')

    
def add_to_cart(request, product_id):
    """
    Add a product to the cart.
    If the product is already in the cart, update the quantity.
    If the product is not in the cart, create a new cart item.
    If the user is authenticated, use the Cart model.
    If the user is not authenticated, use the session to store cart items.
    """
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
    else:
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
        request.session['cart'] = cart

    return redirect('products_list')


