from django.contrib import admin
from django.utils import timezone
from .models import NewsletterSubscription

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'consented', 'consent_date', 'created_at')
    list_filter = ('consented', 'consent_date', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('consented', 'consent_date', 'created_at')
    
    