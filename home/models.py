from django.db import models
# Create your models here.

class InstagramPost(models.Model):
    """
    Model to store Instagram posts for the homepage.
    """
    instagram_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100)
    image_url = models.URLField()
    permalink = models.URLField()
    caption = models.TextField(blank=True, null=True)
    approved = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-featured', '-created_at']