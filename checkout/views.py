from django.conf import settings
from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product
from .forms import CheckoutForm
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutView(TemplateView):
    template_name = 'checkout/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CheckoutForm()
        cart = self.request.session.get('cart', {})
        cart_total = sum(
            item.get('quantity', 1) * Product.objects.get(pk=item['product']).price
            for item in cart.values() if isinstance(item, dict)
        )
        intent = stripe.PaymentIntent.create(
            amount=int(cart_total * 100),  # in centesimi
            currency='eur',
            metadata={'user_id': self.request.user.id}
        )
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        context['client_secret'] = intent.client_secret
        context['cart_total'] = cart_total
        return context

    def post(self, request, *args, **kwargs):
        """
        Process the checkout form submission
        """
        form = CheckoutForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email_address']
            full_name = form.cleaned_data['full_name']
            phone_number = form.cleaned_data.get('phone_number', '')
            street_address1 = form.cleaned_data['street_address1']
            street_address2 = form.cleaned_data.get('street_address2', '')
            town_or_city = form.cleaned_data['town_or_city']
            postcode = form.cleaned_data.get('postcode', '')
            country = form.cleaned_data['country']

            return redirect('success')
        else:
            # SHows errors if the form is not valid
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

def success(request):
    return render(request, 'checkout/success.html')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return HttpResponse(status=400)
    # Gestisci l'evento di pagamento riuscito
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Aggiorna l'ordine come pagato
        # ...
    return HttpResponse(status=200)