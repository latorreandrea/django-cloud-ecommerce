from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.views.decorators.http import require_POST

from .forms import NewsletterSubscriptionForm
from .models import NewsletterSubscription
# Create your views here.

@require_POST
def subscribe_to_newsletter(request):
    """
    Handles the subscription to the newsletter.
    """
    form = NewsletterSubscriptionForm(request.POST)
    
    if form.is_valid():
        email = form.cleaned_data['email']
        
        # Check if email already exists
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={
                'consented': True,
                'consent_date': timezone.now()
            }
        )
        
        if not created and not subscription.consented:
            # If user previously unsubscribed, update their consent
            subscription.consented = True
            subscription.consent_date = timezone.now()
            subscription.save()
            
        # Generate unsubscribe token (encoded email)
        unsubscribe_token = urlsafe_base64_encode(force_bytes(email))
        
        # Send confirmation email
        context = {
            'email': email,
            'unsubscribe_url': request.build_absolute_uri(
                f'/newsletter/unsubscribe/{unsubscribe_token}/'
            ),
            'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'BluntTee'
        }
        
        # Render email content from templates
        subject = "Thank you for subscribing to our newsletter!"
        message = render_to_string('newsletter/emails/subscription_message.txt', context)
        html_message = render_to_string('newsletter/emails/subscription_message.html', context)
        
        # Send email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False,
        )
        
        messages.success(request, 'Thank you for subscribing to our newsletter!')
    else:
        messages.error(request, 'Please enter a valid email address.')
    
    return redirect('home')

def unsubscribe_from_newsletter(request, token):
    try:
        email = force_str(urlsafe_base64_decode(token))
        subscription = get_object_or_404(NewsletterSubscription, email=email)
        
        subscription.consented = False
        subscription.consent_date = timezone.now()
        subscription.save()
        
        messages.success(request, 'You have been successfully unsubscribed.')
    except Exception:
        messages.error(request, 'Invalid unsubscribe link.')
    
    return render(request, 'newsletter/unsubscribe_confirmation.html')