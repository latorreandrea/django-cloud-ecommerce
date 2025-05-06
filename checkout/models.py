from django.db import models
from django.conf import settings
from products.models import Product
from django_countries.fields import CountryField
# Create your models here.


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Shipment Info
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
    # Billing Info
    billing_full_name = models.CharField(max_length=50, blank=True)
    billing_email_address = models.CharField(max_length=100, blank=True)
    billing_phone_number = models.CharField(max_length=20, blank=True)
    billing_street_address1 = models.CharField(max_length=40, blank=True)
    billing_street_address2 = models.CharField(max_length=40, blank=True)
    billing_town_or_city = models.CharField(max_length=40, blank=True)
    billing_county = models.CharField(max_length=40, blank=True)
    billing_postcode = models.CharField(max_length=20, blank=True)
    billing_country = CountryField(blank=True)


class OrderItem(models.Model):
    """Items within an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.ForeignKey('products.Color', on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey('products.Size', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in order {self.order.id}"

class EventLog(models.Model):
    """Log of Stripe webhook events"""
    stripe_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    processed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.event_type} - {self.stripe_id}"