from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from products.models import Product
from cart.models import Cart, CartItem
from .forms import OrderForm
from .models import Order
import stripe
import time
import uuid

# Configure Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutView(TemplateView):
    """
    View to handle the checkout process.
    Displays the checkout form and processes form submissions.
    Creates Stripe payment intents and handles order completion.
    """
    template_name = 'checkout/checkout.html'
    
    def get_context_data(self, **kwargs):
        """
        Prepare the context data for the checkout page.
        Calculates cart total and creates a Stripe payment intent.        
        """
        context = super().get_context_data(**kwargs)
        context['form'] = OrderForm()
        
        # Calculate cart total based on user type (authenticated or session)
        cart_total = self._calculate_cart_total()
        
        # Ensure minimum amount for Stripe (0.50 in most currencies)
        if cart_total < 0.50 and cart_total > 0:
            cart_total = 0.50
            
        # If cart is empty, don't create payment intent
        if cart_total <= 0:
            context['empty_cart'] = True
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        context['cart_total'] = 0
        return context
        
    
    def _calculate_cart_total(self):
        """
        Calculate the total cost of items in the cart.
        Handles both authenticated users (database) and non-authenticated users (session).
        
        Returns:
            float: Total cost of items in the cart
        """
        cart_total = 0
        
        if self.request.user.is_authenticated:
            # For authenticated users - use CartItem from database
            try:
                cart = Cart.objects.get(user=self.request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                cart_total = sum(
                    item.quantity * item.product.price
                    for item in cart_items
                )
            except Cart.DoesNotExist:
                cart_total = 0
        else:
            # For non-authenticated users - use the session
            cart = self.request.session.get('cart', {})
            try:
                cart_total = sum(
                    item.get('quantity', 1) * Product.objects.get(pk=item['product']).price
                    for item in cart.values() if isinstance(item, dict) and 'product' in item
                )
            except (KeyError, Product.DoesNotExist):
                cart_total = 0
                
        return cart_total

    def post(self, request, *args, **kwargs):
        """
        Process the checkout form submission.
        Saves order information and redirects to success page.
        
        Returns:
            HttpResponse: Redirect to success page or form with errors
        """
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            
            # Set user if authenticated
            if request.user.is_authenticated:
                order.user = request.user
                
            # Handle billing address
            billing_different = request.POST.get('billing_different') == 'on'
            if not billing_different:
                # Copy shipping address to billing fields
                order.billing_full_name = order.full_name
                order.billing_email_address = order.email_address
                order.billing_phone_number = order.phone_number
                order.billing_street_address1 = order.street_address1
                order.billing_street_address2 = order.street_address2
                order.billing_town_or_city = order.town_or_city
                order.billing_county = order.county
                order.billing_postcode = order.postcode
                order.billing_country = order.country
            
            # Set status to pending
            order.status = 'pending'
            order.save()
            
            # Create order items from cart
            self.create_order_items(order, request)
            
            # Create or update payment intent
            cart_total = self._calculate_cart_total()
            if cart_total > 0:
                try:
                    intent = stripe.PaymentIntent.create(
                        amount=int(cart_total * 100),
                        currency='eur',
                        metadata={
                            'order_id': order.id
                        }
                    )
                    order.stripe_payment_intent = intent.id
                    order.save()
                except stripe.error.StripeError as e:
                    messages.error(request, "Payment processing error. Please try again.")
                    return redirect('checkout')
            
            # Save payment intent ID if provided
            payment_intent_id = request.POST.get('payment_intent_id')
            if payment_intent_id:
                order.stripe_payment_intent = payment_intent_id
                # Note: Order stays as 'pending' until webhook confirms payment
                order.save()
            
            # Redirect to success page
            messages.success(request, "Order received. We're processing your payment!")
            return redirect('checkout_success')
        else:
            # Return the form with errors
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)


    def create_order_items(self, order, request):
        """Save cart items to order items"""
        if request.user.is_authenticated:
            # For authenticated users
            try:
                cart = Cart.objects.get(user=request.user)
                for item in CartItem.objects.filter(cart=cart):
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                        color=item.color,
                        size=item.size
                    )
            except Cart.DoesNotExist:
                pass
        else:
            # For non-authenticated users
            cart = request.session.get('cart', {})
            for key, item_data in cart.items():
                try:
                    product_id = int(item_data.get('product'))
                    product = Product.objects.get(id=product_id)
                    color_id = item_data.get('color')
                    size_id = item_data.get('size')
                    
                    # Get color and size objects if IDs are provided
                    color = None
                    size = None
                    if color_id:
                        color = Color.objects.filter(id=color_id).first()
                    if size_id:
                        size = Size.objects.filter(id=size_id).first()
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item_data.get('quantity', 1),
                        price=product.price,
                        color=color,
                        size=size
                    )
                except (KeyError, Product.DoesNotExist, ValueError):
                    # Skip invalid items
                    continue


@require_POST
def create_order(request):
    """
    Create order and payment intent before payment is processed.
    Returns JSON with client_secret and order_id.
    """
    form = OrderForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    
    # Create order
    order = form.save(commit=False)
    
    # Set user if authenticated
    if request.user.is_authenticated:
        order.user = request.user
    
    # Handle billing address
    billing_different = request.POST.get('billing_different') == 'on'
    if not billing_different:
        # Copy shipping address to billing fields
        order.billing_full_name = order.full_name
        order.billing_email_address = order.email_address
        order.billing_phone_number = order.phone_number
        order.billing_street_address1 = order.street_address1
        order.billing_street_address2 = order.street_address2
        order.billing_town_or_city = order.town_or_city
        order.billing_county = order.county
        order.billing_postcode = order.postcode
        order.billing_country = order.country
    
    # Set status to pending
    order.status = 'pending'
    order.save()
    
    # Handle order items
    cart_total = 0
    
    # Create order items from cart
    if request.user.is_authenticated:
        # For authenticated users
        try:
            cart = Cart.objects.get(user=request.user)
            for item in CartItem.objects.filter(cart=cart):
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    color=item.color,
                    size=item.size
                )
                cart_total += item.quantity * item.product.price
        except Cart.DoesNotExist:
            pass
    else:
        # For non-authenticated users
        cart = request.session.get('cart', {})
        for key, item_data in cart.items():
            try:
                product_id = int(item_data.get('product'))
                product = Product.objects.get(id=product_id)
                quantity = int(item_data.get('quantity', 1))
                color_id = item_data.get('color')
                size_id = item_data.get('size')
                
                # Get color and size objects if IDs are provided
                color = None
                size = None
                if color_id:
                    from products.models import Color
                    color = Color.objects.filter(id=color_id).first()
                if size_id:
                    from products.models import Size
                    size = Size.objects.filter(id=size_id).first()
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                    color=color,
                    size=size
                )
                cart_total += quantity * product.price
            except (KeyError, Product.DoesNotExist, ValueError):
                continue
    
    # Ensure minimum amount for Stripe
    if cart_total < 0.50 and cart_total > 0:
        cart_total = 0.50
    
    try:
        # Create a unique idempotency key for the payment intent
        idempotency_key = f"order_{int(time.time())}_{uuid.uuid4()}"
        # Create payment intent with order ID in metadata        
        intent = stripe.PaymentIntent.create(
            amount=int(cart_total * 100),
            currency='eur',
            metadata={
                'order_id': order.id,
                'user_id': request.user.id if request.user.is_authenticated else 'anonymous'
            },
            # Ensure the payment intent is unique
            idempotency_key=idempotency_key
            setup_future_usage='off_session',
        )
        
        # Save the payment intent ID to the order
        order.stripe_payment_intent = intent.id
        order.save()
        
        # Return the client secret and order ID
        return JsonResponse({
            'client_secret': intent.client_secret,
            'order_id': order.id
        })
    except stripe.error.StripeError as e:
        # Delete the order if payment intent creation fails
        order.delete()
        return JsonResponse({'error': str(e)}, status=400)


class CheckoutSuccessView(TemplateView):
    """
    Display order confirmation after successful checkout.
    """
    template_name = 'checkout/success.html'