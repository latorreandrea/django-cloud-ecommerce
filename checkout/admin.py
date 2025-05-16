from django.contrib import admin
from .models import Order

# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status')
    list_filter = ('user', 'status')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)