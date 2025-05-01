from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .models import Cart, CartItem, Wishlist, WishlistItem

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

# wishlist management
@login_required
def wishlist_view(request):
    """
    View the wishlist.
    """
    wishlist = getattr(request.user, 'wishlist', None)
    items = wishlist.items.select_related('product') if wishlist else []
    return render(request, 'cart/wishlist.html', {'wishlist_items': items})


@login_required
def toggle_wishlist(request, product_id):
    """
    Toggle a product in the wishlist.
    If the product is already in the wishlist, remove it.
    If the product is not in the wishlist, add it.
    """
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
    if item:
        item.delete()
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
    return redirect('product_detail', pk=product.id)
