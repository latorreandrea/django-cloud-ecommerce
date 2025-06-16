from django.db import models
from django.utils import timezone

class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    consented = models.BooleanField(default=True)
    consent_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
# Create your models here.
