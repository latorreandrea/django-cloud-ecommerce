from django.db import models
from django.contrib.auth.models import User # Import the User model from DjangoAuth
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.CharField(max_length=100, blank=True, default="", null=True)
    country = models.CharField(max_length=40, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    town_or_city = models.CharField(max_length=40, blank=True, null=True)
    street_address1 = models.CharField(max_length=40, blank=True, null=True)
    street_address2 = models.CharField(max_length=40, blank=True, null=True)
    county = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile
    """
    if created:
        Account.objects.create(user=instance)
    else:
        instance.account.save()