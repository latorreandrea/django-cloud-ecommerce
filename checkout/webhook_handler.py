from django.utils import timezone
from datetime import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order, EventLog
from cart.models import Cart, CartItem


def send_order_confirmation(order):
    """Send order confirmation email"""
    subject = f'Order Confirmation #{order.id}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.email_address
    
    # Render email template
    context = {
        'order': order,
        'contact_email': settings.DEFAULT_FROM_EMAIL,
    }
    message = render_to_string('checkout/emails/order_confirmation.txt', context)
    html_message = render_to_string('checkout/emails/order_confirmation.html', context)
    
    # Send email
    send_mail(subject, message, from_email, [to_email], html_message=html_message, fail_silently=True)


def handle_payment_succeeded(event):
    """
    Handle successful payment events from Stripe.
    This function updates the order status in the database,
    empties the cart, and sends a confirmation email.
    """
    payment_intent = event['data']['object']
    order_id = payment_intent['metadata'].get('order_id')
    try:
        order = Order.objects.get(id=order_id)

        pi_retrieve = stripe.PaymentIntent.retrieve(payment_intent['id'])
        # Check if the payment intent status isn't succeeded
        if pi_retrieve.status != 'succeeded':
            print(f"Warning: Payment intent {payment_intent['id']} has status {pi_retrieve.status} in Stripe API!")
            return
        
        if not order.paid:  # Prevent duplicates
            # Mark as paid
            order.paid = True
            order.status = 'paid'
            order.payment_date = timezone.now()
            order.save()

            # Register details of the payment
            payment_details = {
                'stripe_id': payment_intent['id'],
                'amount': payment_intent['amount'] / 100,  # Convert from cents
                'payment_method': payment_intent.get('payment_method_types', ['unknown'])[0],
                'created': datetime.fromtimestamp(payment_intent['created']),
                'currency': payment_intent['currency'],
            }
            # Empty the cart
            if order.user:
                try:
                    cart = Cart.objects.get(user=order.user)
                    CartItem.objects.filter(cart=cart).delete()
                except Cart.DoesNotExist:
                    pass
            
            # Send confirmation email
            send_order_confirmation(order)
            
    except Order.DoesNotExist:
        # Log error
        print(f"Error: Order with ID {order_id} not found.")
    except stripe.error.StripeError as e:
        # Log stripe error
        print(f"Stripe error: {str(e)}")



def handle_payment_failed(event):
    """Handle failed payment events from Stripe"""
    payment_intent = event['data']['object']
    order_id = payment_intent['metadata'].get('order_id')
    
    try:
        order = Order.objects.get(id=order_id)
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        # Optionally notify the customer
    except Order.DoesNotExist:
        # Log error
        print(f"Error: Order with ID {order_id} not found.")


def handle_stripe_event(event):
    """
    Handle incoming Stripe events.
    This function processes different types of events from Stripe
    and updates the database accordingly.
    """
    event_id = event['id']
    event_type = event['type']
    
    # Check if event has already been processed
    if EventLog.objects.filter(stripe_id=event_id).exists():
        return  # Skip processing
        
    # Log the event
    EventLog.objects.create(stripe_id=event_id, event_type=event_type)
    
    if event_type == 'payment_intent.succeeded':
        handle_payment_succeeded(event)
    elif event_type == 'payment_intent.payment_failed':
        handle_payment_failed(event)

    