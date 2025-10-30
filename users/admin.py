from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  # For advanced User admin features
from .models import User, Payment, Subscription

@admin.register(User)
class UserAdmin(UserAdmin):  # Inherit from UserAdmin for built-in features like search/filter
    list_display = ['id', 'email', 'name', 'role', 'is_staff', 'is_active', 'date_joined']  # What to show in the list
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']  # Filters on the right
    search_fields = ['email', 'name']  # Search by these fields
    ordering = ['email']  # Sort by email
    fieldsets = UserAdmin.fieldsets + (  # Add your custom fields to the edit form
        ('Custom Fields', {
            'fields': ('name', 'phone', 'city', 'avatar', 'role')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (  # For adding new users
        ('Custom Fields', {
            'fields': ('name', 'phone', 'city', 'avatar', 'role')
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_amount', 'payment_type', 'status', 'created_at']
    list_filter = ['status', 'payment_type']
    search_fields = ['user__email', 'stripe_session_id']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user_sub', 'course', 'subscribed_at']
    list_filter = ['subscribed_at']
    search_fields = ['user_sub__email', 'course__title']  # Assuming Course has a 'title' field
