from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin interface"""
    list_display = ['email', 'full_name', 'company', 'role', 'is_verified', 'is_active', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active', 'company__business_sector', 'created_at']
    search_fields = ['email', 'full_name', 'company__name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': (
            'full_name', 'phone_number', 'job_title', 'department'
        )}),
        ('Company', {'fields': ('company', 'role')}),
        ('Permissions', {'fields': (
            'is_active', 'is_verified', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'
        )}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Preferences', {'fields': ('preferences',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')




@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Password reset tokens admin interface"""
    list_display = ['user', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')