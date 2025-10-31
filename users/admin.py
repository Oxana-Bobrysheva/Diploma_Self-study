from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  # For advanced User admin features
from .models import User

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
