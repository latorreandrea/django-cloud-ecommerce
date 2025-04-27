from django.contrib import admin
from .models import UserProfile
# Register your models here.




class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    list_display = ('full_name', 'email', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')
    ordering = ('date_joined',)
    readonly_fields = ('last_login',)

admin.site.register(UserProfile, UserProfileAdmin)