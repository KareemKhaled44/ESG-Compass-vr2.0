from django.contrib import admin
from django.utils.html import format_html
from .models import Company, Location, CompanySettings, CompanyInvitation


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Company admin interface"""
    list_display = [
        'name', 'business_sector', 'employee_size', 'emirate',
        'total_users', 'setup_step', 'esg_scoping_completed',
        'overall_esg_score', 'created_at'
    ]
    list_filter = [
        'business_sector', 'employee_size', 'emirate', 'license_type',
        'esg_scoping_completed', 'onboarding_completed', 'created_at'
    ]
    search_fields = ['name', 'main_location']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'business_sector', 'employee_size')
        }),
        ('Location', {
            'fields': ('main_location', 'emirate', 'license_type')
        }),
        ('ESG Setup', {
            'fields': ('setup_step', 'esg_scoping_completed', 'onboarding_completed')
        }),
        ('ESG Scores', {
            'fields': (
                'overall_esg_score', 'environmental_score', 
                'social_score', 'governance_score'
            )
        }),
        ('Progress Tracking', {
            'fields': (
                'data_completion_percentage', 'evidence_completion_percentage',
                'total_fields', 'completed_fields', 'total_evidence_files',
                'uploaded_evidence_files'
            )
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def total_users(self, obj):
        """Display total number of users"""
        count = obj.users.count()
        return format_html(
            '<a href="/admin/authentication/user/?company__id__exact={}">{}</a>',
            obj.id, count
        )
    total_users.short_description = 'Users'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Location admin interface"""
    list_display = [
        'name', 'company', 'emirate', 'building_type',
        'is_primary', 'total_floor_area', 'created_at'
    ]
    list_filter = [
        'emirate', 'building_type', 'ownership_type',
        'is_primary', 'has_separate_meters', 'created_at'
    ]
    search_fields = ['name', 'company__name', 'address']
    ordering = ['company__name', '-is_primary', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'name', 'address', 'emirate')
        }),
        ('Building Details', {
            'fields': (
                'total_floor_area', 'number_of_floors', 
                'building_type', 'ownership_type'
            )
        }),
        ('Operations', {
            'fields': (
                'operating_hours', 'number_of_employees',
                'has_separate_meters', 'is_primary'
            )
        }),
        ('Utility Information', {
            'fields': ('meters_info',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    """Company settings admin interface"""
    list_display = [
        'company', 'default_report_frequency', 'email_notifications',
        'task_reminders', 'report_reminders', 'updated_at'
    ]
    list_filter = [
        'default_report_frequency', 'email_notifications',
        'task_reminders', 'report_reminders'
    ]
    search_fields = ['company__name']
    ordering = ['company__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Company', {
            'fields': ('company',)
        }),
        ('Reporting Preferences', {
            'fields': ('default_report_frequency',)
        }),
        ('Notifications', {
            'fields': (
                'email_notifications', 'task_reminders', 'report_reminders'
            )
        }),
        ('Frameworks & Targets', {
            'fields': ('active_frameworks', 'targets'),
            'classes': ('collapse',)
        }),
        ('Custom Configuration', {
            'fields': ('custom_fields',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')


@admin.register(CompanyInvitation)
class CompanyInvitationAdmin(admin.ModelAdmin):
    """Company invitation admin interface"""
    list_display = [
        'email', 'company', 'role', 'status',
        'invited_by', 'created_at', 'expires_at'
    ]
    list_filter = ['status', 'role', 'created_at', 'expires_at']
    search_fields = ['email', 'company__name', 'invited_by__email']
    ordering = ['-created_at']
    readonly_fields = ['id', 'token', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Invitation Details', {
            'fields': ('company', 'email', 'role', 'message')
        }),
        ('Status', {
            'fields': ('status', 'invited_by', 'accepted_by', 'accepted_at')
        }),
        ('Security', {
            'fields': ('token', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'invited_by', 'accepted_by'
        )