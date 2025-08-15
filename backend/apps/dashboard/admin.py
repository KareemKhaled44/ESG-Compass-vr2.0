from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import DashboardMetric, DashboardWidget, DashboardAlert, BenchmarkData, AnalyticsEvent


@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    """Dashboard metric admin interface"""
    list_display = [
        'metric_name', 'company', 'metric_type', 'period_display',
        'is_current', 'calculated_at'
    ]
    list_filter = [
        'metric_type', 'is_current', 'calculated_at',
        'period_start', 'period_end'
    ]
    search_fields = ['metric_name', 'company__name']
    ordering = ['-calculated_at']
    readonly_fields = ['id', 'calculated_at']
    
    fieldsets = (
        ('Metric Information', {
            'fields': ('company', 'metric_type', 'metric_name', 'metric_value')
        }),
        ('Time Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Calculation Details', {
            'fields': ('calculated_by', 'is_current', 'version')
        }),
        ('Metadata', {
            'fields': ('id', 'calculated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'calculated_by')
    
    def period_display(self, obj):
        """Display period range"""
        return f"{obj.period_start} to {obj.period_end}"
    period_display.short_description = 'Period'


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """Dashboard widget admin interface"""
    list_display = [
        'title', 'company', 'widget_type', 'position_display',
        'is_visible', 'refresh_interval_minutes', 'last_refreshed'
    ]
    list_filter = [
        'widget_type', 'is_visible', 'refresh_interval_minutes',
        'created_at', 'updated_at'
    ]
    search_fields = ['title', 'description', 'company__name']
    ordering = ['company', 'position_y', 'position_x']
    readonly_fields = ['id', 'last_refreshed', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Widget Information', {
            'fields': ('company', 'widget_type', 'title', 'description')
        }),
        ('Layout', {
            'fields': ('position_x', 'position_y', 'width', 'height')
        }),
        ('Configuration', {
            'fields': ('settings', 'refresh_interval_minutes')
        }),
        ('Visibility', {
            'fields': ('is_visible', 'visible_to_roles')
        }),
        ('Metadata', {
            'fields': ('id', 'last_refreshed', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')
    
    def position_display(self, obj):
        """Display widget position"""
        return f"({obj.position_x}, {obj.position_y}) - {obj.width}x{obj.height}"
    position_display.short_description = 'Position & Size'


@admin.register(DashboardAlert)
class DashboardAlertAdmin(admin.ModelAdmin):
    """Dashboard alert admin interface"""
    list_display = [
        'title', 'company', 'alert_type', 'severity',
        'is_active', 'is_read', 'read_by_display', 'created_at'
    ]
    list_filter = [
        'alert_type', 'severity', 'is_active', 'is_read',
        'action_required', 'created_at'
    ]
    search_fields = ['title', 'message', 'company__name']
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'is_expired', 'created_at', 'read_at'
    ]
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('company', 'alert_type', 'title', 'message', 'severity')
        }),
        ('Related Objects', {
            'fields': ('related_task', 'related_assessment'),
            'classes': ('collapse',)
        }),
        ('Alert Status', {
            'fields': ('is_active', 'is_read', 'read_by', 'expires_at')
        }),
        ('Action', {
            'fields': ('action_required', 'action_url', 'action_text')
        }),
        ('Metadata', {
            'fields': ('id', 'is_expired', 'created_at', 'read_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'deactivate_alerts']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'read_by', 'related_task', 'related_assessment'
        )
    
    def read_by_display(self, obj):
        """Display who read the alert"""
        if obj.read_by:
            return obj.read_by.full_name
        return '-'
    read_by_display.short_description = 'Read By'
    
    def mark_as_read(self, request, queryset):
        """Mark selected alerts as read"""
        for alert in queryset:
            if not alert.is_read:
                alert.mark_read(request.user)
        self.message_user(request, f"Marked {queryset.count()} alerts as read.")
    mark_as_read.short_description = "Mark selected alerts as read"
    
    def mark_as_unread(self, request, queryset):
        """Mark selected alerts as unread"""
        updated = queryset.update(
            is_read=False,
            read_by=None,
            read_at=None
        )
        self.message_user(request, f"Marked {updated} alerts as unread.")
    mark_as_unread.short_description = "Mark selected alerts as unread"
    
    def deactivate_alerts(self, request, queryset):
        """Deactivate selected alerts"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} alerts.")
    deactivate_alerts.short_description = "Deactivate selected alerts"


@admin.register(BenchmarkData)
class BenchmarkDataAdmin(admin.ModelAdmin):
    """Benchmark data admin interface"""
    list_display = [
        'benchmark_name', 'sector', 'region', 'overall_average',
        'sample_size', 'is_current', 'updated_at'
    ]
    list_filter = [
        'sector', 'region', 'is_current', 'data_source', 'updated_at'
    ]
    search_fields = ['benchmark_name', 'sector', 'region', 'data_source']
    ordering = ['-updated_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Benchmark Information', {
            'fields': ('benchmark_name', 'sector', 'region', 'data_source', 'data_period')
        }),
        ('ESG Averages', {
            'fields': (
                'environmental_average', 'social_average',
                'governance_average', 'overall_average'
            )
        }),
        ('Statistical Data', {
            'fields': (
                'sample_size', 'percentile_25',
                'percentile_50', 'percentile_75'
            )
        }),
        ('Status', {
            'fields': ('is_current',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for existing objects"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.extend(['sector', 'region', 'benchmark_name'])
        return readonly


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    """Analytics event admin interface"""
    list_display = [
        'event_type', 'company', 'user_display', 'ip_address', 'created_at'
    ]
    list_filter = [
        'event_type', 'created_at'
    ]
    search_fields = [
        'company__name', 'user__full_name', 'event_type', 
        'ip_address', 'user_agent'
    ]
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('company', 'user', 'event_type', 'event_data')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'referrer')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'user')
    
    def user_display(self, obj):
        """Display user name or anonymous"""
        if obj.user:
            return obj.user.full_name
        return 'Anonymous'
    user_display.short_description = 'User'
    
    def has_add_permission(self, request):
        """Disable manual creation of analytics events"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of analytics events"""
        return False


# Inline admin classes for related models

class DashboardMetricInline(admin.TabularInline):
    """Inline for dashboard metrics"""
    model = DashboardMetric
    extra = 0
    readonly_fields = ['calculated_at']
    fields = ['metric_type', 'metric_name', 'is_current', 'calculated_at']


class DashboardAlertInline(admin.TabularInline):
    """Inline for dashboard alerts"""
    model = DashboardAlert
    extra = 0
    readonly_fields = ['created_at', 'is_expired']
    fields = ['alert_type', 'title', 'severity', 'is_active', 'is_read', 'created_at']


class AnalyticsEventInline(admin.TabularInline):
    """Inline for analytics events"""
    model = AnalyticsEvent
    extra = 0
    readonly_fields = ['event_type', 'created_at']
    fields = ['event_type', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False