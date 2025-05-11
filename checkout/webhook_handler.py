from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Order, OrderItem, PendingOrder, EventLog
from cart.models import Cart, CartItem
from products.models import Product, Color, Size

import stripe
import json
import logging

logger = logging.getLogger(__name__)


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


def handle_payment_succeeded(event):
    """   
    Handle the payment succeeded event from Stripe.
    This function creates an order in the database from the pending order data.    
    """
    payment_intent = event['data']['object']
    pending_order_id = payment_intent['metadata'].get('pending_order_id')

    logger.info(f"Webhook payment_succeeded received for pending_order_id: {pending_order_id}")

    try:
        # Retrieve the pending order
        pending_order = PendingOrder.objects.get(id=pending_order_id)

        # Retrieve the order and item data
        order_data = pending_order.order_data
        items_data = pending_order.items_data

        # Create the real order
        order = Order(
            full_name=order_data['full_name'],
            email_address=order_data['email_address'],
            phone_number=order_data['phone_number'],
            country=order_data['country'],
            postcode=order_data['postcode'],
            town_or_city=order_data['town_or_city'],
            street_address1=order_data['street_address1'],
            street_address2=order_data.get('street_address2', ''),
            county=order_data.get('county', ''),
            billing_full_name=order_data.get('billing_full_name', ''),
            billing_email_address=order_data.get('billing_email_address', ''),
            billing_phone_number=order_data.get('billing_phone_number', ''),
            billing_country=order_data.get('billing_country', ''),
            billing_postcode=order_data.get('billing_postcode', ''),
            billing_town_or_city=order_data.get('billing_town_or_city', ''),
            billing_street_address1=order_data.get('billing_street_address1', ''),
            billing_street_address2=order_data.get('billing_street_address2', ''),
            billing_county=order_data.get('billing_county', ''),
            subtotal=order_data['order_total'],
            shipping_cost=order_data['shipping_cost'],
            total=order_data['grand_total'], 
            stripe_payment_intent=payment_intent['id'],
            status='paid',
            paid=True,
            payment_date=timezone.now()
        )

        # Add the user if available
        if 'user_id' in order_data:
            try:
                user = get_user_model().objects.get(id=order_data['user_id'])
                order.user = user
            except get_user_model().DoesNotExist:
                pass
        
        order.save()

        # Create the order items
        for item_data in items_data:
            try:
                product = Product.objects.get(id=item_data['product_id'])

                # Set color and size if present
                color = None
                size = None
                if 'color_id' in item_data:
                    try:
                        color = Color.objects.get(id=item_data['color_id'])
                    except Color.DoesNotExist:
                        pass
                
                if 'size_id' in item_data:
                    try:
                        size = Size.objects.get(id=item_data['size_id'])
                    except Size.DoesNotExist:
                        pass
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    price=item_data['price'],
                    color=color,
                    size=size
                )
            except Product.DoesNotExist:
                logger.warning(f"Prodotto con ID {item_data['product_id']} non trovato")
                continue
        
        # Delete the pending order
        pending_order.delete()

        # Empty the cart for authenticated users
        user_id = payment_intent['metadata'].get('user_id')
        if user_id and user_id != 'anonymous':
            try:
                user = get_user_model().objects.get(id=user_id)
                cart = Cart.objects.get(user=user)
                CartItem.objects.filter(cart=cart).delete()
                logger.info(f"Carrello svuotato per l'utente {user_id}.")
            except (get_user_model().DoesNotExist, Cart.DoesNotExist):
                logger.warning(f"Impossibile trovare l'utente o il carrello per user_id: {user_id}")
        
        # Send order confirmation email
        send_order_confirmation(order)
        
        logger.info(f"Ordine {order.id} creato con successo dal pending order {pending_order_id}")
        return HttpResponse(status=200)
    
    except PendingOrder.DoesNotExist:
        logger.error(f"PendingOrder con ID {pending_order_id} non trovato.")
        return HttpResponse(status=404)
    except Exception as e:
        logger.error(f"Errore nel processare il payment_succeeded webhook: {str(e)}", exc_info=True)
        return HttpResponse(status=500)


def send_order_confirmation(order):
    """
    Send an order confirmation email to the customer.
    """
    subject = f'Order confirmation {order.id}'
    message = render_to_string(
        'checkout/confirmation_emails/confirmation_email.txt',
        {'order': order}
    )
    email_from = settings.DEFAULT_FROM_EMAIL
    email_to = [order.email_address]
    
    send_mail(
        subject,
        message,
        email_from,
        email_to,
        fail_silently=False,
    )

    logger.info(f"Confirmation email sent for order {order.id}")


def handle_payment_failed(event):
    """Handle failed payment events from Stripe"""
    payment_intent = event['data']['object']
    pending_order_id = payment_intent['metadata'].get('pending_order_id')
    user_id = payment_intent['metadata'].get('user_id')
    
    logger.warning(f"Payment failed for pending order ID: {pending_order_id}, user ID: {user_id}")
    
    try:
        # Get the pending order
        pending_order = PendingOrder.objects.get(id=pending_order_id)
        
        # For debugging, log some details about the failed payment
        failure_message = payment_intent.get('last_payment_error', {}).get('message', 'Unknown reason')
        logger.info(f"Payment failed reason: {failure_message}")
        
        # Don't need to create an order since payment failed
        # Just delete the pending order
        pending_order.delete()
        logger.info(f"Deleted pending order {pending_order_id} after payment failure")
        
        # You could store the failure in a PaymentFailureLog model if needed
        # PaymentFailureLog.objects.create(
        #     user_id=user_id if user_id != 'anonymous' else None,
        #     payment_intent_id=payment_intent['id'],
        #     failure_reason=failure_message
        # )
        
        return HttpResponse(status=200)
    except PendingOrder.DoesNotExist:
        logger.error(f"PendingOrder with ID {pending_order_id} not found for failed payment.")
        return HttpResponse(status=404)
    except Exception as e:
        logger.error(f"Error processing payment_failed webhook: {str(e)}", exc_info=True)
        return HttpResponse(status=500)



    