from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST 
from django.http import HttpResponse
from django.conf import settings
import stripe
from .webhook_handler import handle_stripe_event

@require_POST
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        # Log debug
        print(f"Webhook received: {event['type']}")

        # Use handle_stripe_event to process the event
        try:
            handle_stripe_event(event)
        except Exception as e:
            print(f"Error processing webhook: {e}")
            # Log error but still return 200 to avoid Stripe retrying
            return HttpResponse(f"Error processing webhook: {e}", status=200)
        
        return HttpResponse(status=200)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)