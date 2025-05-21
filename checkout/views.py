from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from products.models import Product, Color, Size, ProductImage
from cart.models import Cart, CartItem
from .forms import OrderForm
from .models import Order, OrderItem, PendingOrder
import stripe
import time
from datetime import timedelta
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
        # Get cart items
        cart_items = []
        # For authenticated users
        if self.request.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=self.request.user)
                for item in CartItem.objects.filter(cart=cart):
                    # Get image URL correctly
                    image_url = None
                    if item.color:
                        product_image = ProductImage.objects.filter(
                            product=item.product, 
                            color=item.color
                        ).first()
                        if product_image:
                            image_url = product_image.small_image
                    
                    cart_items.append({
                        'product': item.product,
                        'color': item.color,
                        'size': item.size,
                        'quantity': item.quantity,
                        'price': item.product.price * item.quantity,
                        'image_url': image_url,
                    })
            except Cart.DoesNotExist:
                pass
        # For non-authenticated users
        else:
            cart = self.request.session.get('cart', {})
            for key, item_data in cart.items():
                try:
                    product_id = int(item_data.get('product'))
                    product = Product.objects.get(id=product_id)
                    quantity = int(item_data.get('quantity', 1))
                    color_id = item_data.get('color')
                    size_id = item_data.get('size')
                    
                    # Find color and size
                    color = None
                    size = None
                    image_url = None
                    
                    if color_id:
                        color = Color.objects.filter(id=color_id).first()
                        if color:
                            product_image = ProductImage.objects.filter(
                                product=product,
                                color=color
                            ).first()
                            if product_image:
                                image_url = product_image.small_image
                                
                    if size_id:
                        size = Size.objects.filter(id=size_id).first()

                    cart_items.append({
                        'product': product,
                        'color': color,
                        'size': size,
                        'quantity': quantity,
                        'price': product.price * quantity,  # Prezzo * quantità
                        'image_url': image_url,
                    })
                except (Product.DoesNotExist, ValueError, TypeError, KeyError):
                    pass
                    
        # Calculate subtotal from cart
        cart_subtotal = self._calculate_cart_total()
        
        # Calculate shipping cost
        shipping_cost = self._calculate_shipping_cost(cart_items)
        
        # Calculate total (products + shipping)
        cart_total = cart_subtotal + shipping_cost

        # Calulate number of product for free shipping
        items_for_free_shipping = max(0, 5 - len(cart_items))
        
        # Add to context
        context['cart_items'] = cart_items
        context['cart_subtotal'] = cart_subtotal
        context['shipping_cost'] = shipping_cost
        context['cart_total'] = cart_total
        context['items_for_free_shipping'] = items_for_free_shipping
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        
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

    def _calculate_shipping_cost(self, cart_items):
        """
        Calculate shipping cost based on total quantity of products:
        - 1 product: 10€
        - 2-4 products: 11€
        - 5+ products: free shipping
        
        Args:
            cart_items: List of cart items
        
        Returns:
            float: Shipping cost
        """
        # Somma le quantità di tutti i prodotti
        total_quantity = sum(item.get('quantity', 1) for item in cart_items)
        
        if total_quantity >= 5:
            # Free shipping for 5+ products
            return 0
        elif total_quantity > 1:
            # Base price + 1€ for second product
            return 11
        elif total_quantity == 1:
            # Base price for one product
            return 10
        else:
            # Empty cart
            return 0

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
    Create temporary order and payment intent before payment processing.
    returns JsonResponse with client_secret and pending_order_id.
    """
    form = OrderForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    
    # Extract order data from the form
    order_data = {
        'full_name': form.cleaned_data['full_name'],
        'email_address': form.cleaned_data['email_address'],
        'phone_number': form.cleaned_data['phone_number'],
        'country': str(form.cleaned_data['country']),
        'postcode': form.cleaned_data['postcode'],
        'town_or_city': form.cleaned_data['town_or_city'],
        'street_address1': form.cleaned_data['street_address1'],
        'street_address2': form.cleaned_data['street_address2'],
        'county': form.cleaned_data['county'],
    }
    
    # Managing billing address
    billing_different = request.POST.get('billing_different') == 'on'
    if not billing_different:
        # Copy shipping address to billing fields
        order_data['billing_full_name'] = order_data['full_name']
        order_data['billing_email_address'] = order_data['email_address']
        order_data['billing_phone_number'] = order_data['phone_number']
        order_data['billing_country'] = order_data['country']
        order_data['billing_postcode'] = order_data['postcode']
        order_data['billing_town_or_city'] = order_data['town_or_city']
        order_data['billing_street_address1'] = order_data['street_address1']
        order_data['billing_street_address2'] = order_data['street_address2']
        order_data['billing_county'] = order_data['county']
    else:
        # Use provided billing address
        order_data['billing_full_name'] = form.cleaned_data['billing_full_name']
        order_data['billing_email_address'] = form.cleaned_data['billing_email_address']
        order_data['billing_phone_number'] = form.cleaned_data['billing_phone_number']
        order_data['billing_country'] = str(form.cleaned_data['billing_country'])
        order_data['billing_postcode'] = form.cleaned_data['billing_postcode']
        order_data['billing_town_or_city'] = form.cleaned_data['billing_town_or_city']
        order_data['billing_street_address1'] = form.cleaned_data['billing_street_address1']
        order_data['billing_street_address2'] = form.cleaned_data['billing_street_address2']
        order_data['billing_county'] = form.cleaned_data['billing_county']

    # Add user ID if authenticated
    if request.user.is_authenticated:
        order_data['user_id'] = request.user.id

    # Prepare item data and calculate totals
    items_data = []
    cart_items = []
    cart_subtotal = 0

    if request.user.is_authenticated:
        # For authenticated users
        try:
            cart = Cart.objects.get(user=request.user)
            for item in CartItem.objects.filter(cart=cart):
                item_data = {
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.product.price),
                }
                
                if item.color:
                    item_data['color_id'] = item.color.id
                    item_data['color_name'] = item.color.name
                if item.size:
                    item_data['size_id'] = item.size.id
                    item_data['size_name'] = item.size.name
                
                items_data.append(item_data)
                cart_subtotal += item.quantity * item.product.price
                
                # Add a cart items for shipping calculation
                cart_items.append({
                    'quantity': item.quantity,
                    'price': float(item.product.price * item.quantity)
                })
        except Cart.DoesNotExist:
            pass
    else:
        # For unauthenticated users
        cart = request.session.get('cart', {})
        for key, item_data in cart.items():
            try:
                product_id = int(item_data.get('product'))
                product = Product.objects.get(id=product_id)
                quantity = int(item_data.get('quantity', 1))
                
                item_obj = {
                    'product_id': product_id,
                    'product_name': product.name,
                    'quantity': quantity,
                    'price': float(product.price),
                }
                
                color_id = item_data.get('color')
                size_id = item_data.get('size')
                
                if color_id:
                    color = Color.objects.filter(id=color_id).first()
                    if color:
                        item_obj['color_id'] = color_id
                        item_obj['color_name'] = color.name
                if size_id:
                    size = Size.objects.filter(id=size_id).first()
                    if size:
                        item_obj['size_id'] = size_id
                        item_obj['size_name'] = size.name
                
                items_data.append(item_obj)
                cart_subtotal += quantity * product.price
                
                # Add a cart items for shipping calculation
                cart_items.append({
                    'quantity': quantity,
                    'price': float(product.price * quantity)
                })
            except (KeyError, Product.DoesNotExist, ValueError):
                continue
    
    # Shipping cost is calculated based on the cart items
    view = CheckoutView()
    shipping_cost = view._calculate_shipping_cost(cart_items)
    
    # Saving shipping cost and totals
    order_data['shipping_cost'] = float(shipping_cost)
    order_data['order_total'] = float(cart_subtotal)
    order_data['grand_total'] = float(cart_subtotal + shipping_cost)    

    # Secure minimum amount for Stripe
    cart_total = order_data['grand_total']
    if cart_total < 0.50 and cart_total > 0:
        cart_total = 0.50
    
    try:
        # Create a unique idempotency key
        idempotency_key = f"order_{int(time.time())}_{uuid.uuid4()}"

        # Create a PendingOrder with expiration
        pending_order = PendingOrder(
            order_data=order_data,
            items_data=items_data,
            expires_at=timezone.now() + timedelta(hours=24),  # Expires after 24 hours
        )
        pending_order.save()

        # Create payment intent with pending_order_id in metadata
        intent = stripe.PaymentIntent.create(
            amount=int(cart_total * 100),
            currency='eur',
            metadata={
                'pending_order_id': pending_order.id,
                'user_id': request.user.id if request.user.is_authenticated else 'anonymous'
            },
            idempotency_key=idempotency_key,
            setup_future_usage='off_session',
        )

        # Save the payment intent ID in the pending order
        pending_order.stripe_payment_intent = intent.id
        pending_order.save()

        # Return client secret and pending_order_id
        return JsonResponse({
            'client_secret': intent.client_secret,
            'pending_order_id': pending_order.id
        })
    except stripe.error.StripeError as e:
        # Delete the pending order if the payment intent creation fails
        if 'pending_order' in locals():
            pending_order.delete()
        return JsonResponse({'error': str(e)}, status=400)


class CheckoutSuccessView(TemplateView):
    """
    Display order confirmation after successful checkout.
    """
    template_name = 'checkout/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Verify if payment was successful
        payment_confirmed = self.request.GET.get('payment_confirmed') == 'true'
        order_id = self.request.GET.get('order_id')

        if payment_confirmed:
            context['payment_successful'] = True

            # Get order details if available
            if order_id:
                try:
                    if self.request.user.is_authenticated:
                        order = Order.objects.get(id=order_id, user=self.request.user)
                    else:
                        order = Order.objects.get(id=order_id, email_address=self.request.session.get('email_address', ''))
                    
                    context['order'] = order
                    
                    # Send confirmation email
                    self.send_confirmation_email(order)
                except Order.DoesNotExist:
                    pass

            # Empty the cart
            self._clear_cart()
                
        return context
    
    def send_confirmation_email(self, order):
        """Send confirmation email using the existing template"""
        subject = f'Order NR #{order.id} confirmation '
        
        # Use HTML template
        html_message = render_to_string(
            'checkout/emails/order_confirmation.html',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL}
        )
        
        # Use text template
        plain_message = render_to_string(
            'checkout/emails/order_confirmation.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL}
        )
        
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = order.email_address
        
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False
        )
    
    def _clear_cart(self):
        """Empty the user's cart after a successful checkout"""
        if self.request.user.is_authenticated:
            # for authenticated users
            try:
                cart = Cart.objects.get(user=self.request.user)
                CartItem.objects.filter(cart=cart).delete()
            except Cart.DoesNotExist:
                pass
        else:
            # for non-authenticated users
            if 'cart' in self.request.session:
                del self.request.session['cart']
                self.request.session.modified = True