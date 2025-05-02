from django.db import models
from django.conf import settings
from products.models import Product
from django_countries.fields import CountryField
# Create your models here.


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    full_name = models.CharField(max_length=50, blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    email_address = models.CharField(max_length=100, blank=False, default="")
    country = CountryField()
    postcode = models.CharField(max_length=20, blank=True)
    town_or_city = models.CharField(max_length=40, blank=False)
    street_address1 = models.CharField(max_length=40, blank=False)
    street_address2 = models.CharField(max_length=40, blank=True)
    county = models.CharField(max_length=40, blank=False)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    # altri campi come indirizzo, totale, ecc.

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    # altri campi se servono