from django.db import models
from django.utils import timezone
from checkout.models import Order

class ShirtigoOrder(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shirtigo_order')
    shirtigo_order_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('created', 'Created in Shirtigo'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Shirtigo Order {self.shirtigo_order_id} for Order {self.order.id}"

class ShirtigoAPILog(models.Model):
    shirtigo_order = models.ForeignKey(ShirtigoOrder, on_delete=models.CASCADE, related_name='api_logs')
    request_data = models.JSONField()
    response_data = models.JSONField(blank=True, null=True)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=255)
    
    def __str__(self):
        return f"API Call for {self.shirtigo_order} - {self.success}"