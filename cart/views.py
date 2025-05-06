from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from products.models import Product, Color, Size
from .models import Cart, CartItem, Wishlist, WishlistItem
# use of random to use random messages
import random

# list of messages
FORGOT_COLOR_SIZE_MESSAGES = [
    "We know decisions are hard, but pick a color and a size, fashionista!",
    "Hold up, Picasso! Choose a color and a size before we make this masterpiece yours.",
    "Naked shirts aren't a vibe — give us a color and a size, please!",
    "We’d love to sell you something, but we need to know what it looks like first...",
    "Your shirt is feeling a bit lost. Can you help it find its color and size?",
    "This shirt needs an identity: color? size? Throw it a bone.",
    "Oops! We can't read minds yet — pick a color and a size, pretty please.",
    "You’re halfway to greatness — now just choose a color and a size!",
]

PRODUCT_ADDED_MESSAGES = [
    "Boom! One more glorious item just landed in your cart.",
    "Added to cart — your questionable fashion choices are now one step closer to reality.",
    "Nice pick! It’s chillin’ in your cart now, waiting for checkout glory.",
    "Cart updated! Somewhere, a T-shirt is doing a happy dance.",
    "It’s in the cart! You’re basically a shopping ninja.",
    "That shirt couldn’t resist you. It’s now officially carted.",
    "Into the cart it goes! Your closet’s already whispering thanks.",
    "Success! You’ve just adopted a new piece of fabric with attitude.",
]


# Create your views here.
class CartView(TemplateView):
    """
    View the cart.
    If the user is authenticated, use the Cart model.
    If the user is not authenticated, use the session to store cart items.
    """
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        return context


def add_to_cart(request, product_id):
    """
    Add a product to the cart.
    If the product is already in the cart, increase its quantity.
    If the user is authenticated, use the Cart model.
    If the user is not authenticated, use the session to store cart items.
    """
    product = get_object_or_404(Product, id=product_id)
    color_id = request.POST.get('color_id')
    size_id = request.POST.get('size_id')
    quantity = int(request.POST.get('quantity', 1))

    # Check if color and size are provided
    # If not, show a message and redirect to the product detail page
    if not color_id or not size_id:
        msg = random.choice(FORGOT_COLOR_SIZE_MESSAGES)
        messages.error(request, msg)
        return redirect('product_detail', pk=product_id)

    color = Color.objects.filter(id=color_id).first()
    size = Size.objects.filter(id=size_id).first() 
    
    # Handle authenticated users
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            # Try to find the existing item
            cart_item = CartItem.objects.get(
                cart=cart,
                product=product,
                color=color,
                size=size
            )
            # Update quantity if item exists
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            # Create new item if it doesn't exist
            CartItem.objects.create(
                cart=cart,
                product=product,
                color=color,
                size=size,
                quantity=quantity
            )    
    # Handle non-authenticated users (session)
    else:
        cart = request.session.get('cart', {})
        key = f"{product_id}:{color_id}:{size_id}"
        
        # If the item exists, update quantity
        if key in cart:
            if isinstance(cart[key], dict) and 'quantity' in cart[key]:
                cart[key]['quantity'] += quantity
            else:
                # Fix invalid cart item format
                cart[key] = {
                    'product': product_id,
                    'color': color_id,
                    'size': size_id,
                    'quantity': quantity,
                }
        # If the item doesn't exist, create it
        else:
            cart[key] = {
                'product': product_id,
                'color': color_id,
                'size': size_id,
                'quantity': quantity,
            }
        
        request.session['cart'] = cart
    
    # Show success message
    msg = random.choice(PRODUCT_ADDED_MESSAGES)
    messages.success(request, msg)
    
    return redirect('product_detail', pk=product_id)


def remove_from_cart(request, key):
    """
    Remove an item from the session cart by its key.
    """
    cart = request.session.get('cart', {})
    if key in cart:
        del cart[key]
        request.session['cart'] = cart
    return HttpResponseRedirect(reverse('cart'))


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
