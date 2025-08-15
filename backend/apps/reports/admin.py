from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ReportTemplate, GeneratedReport, ReportSection, ReportSchedule, ReportAccess


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Report template admin interface"""
    list_display = [
        'display_name', 'report_type', 'status', 'version',
        'is_framework_official', 'sections_count', 'updated_at'
    ]
    list_filter = [
        'report_type', 'status', 'is_framework_official',
        'requires_verification', 'created_at'
    ]
    search_fields = ['name', 'display_name', 'description']
    ordering = ['report_type', 'display_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description', 'report_type')
        }),
        ('Configuration', {
            'fields': ('template_config', 'supported_formats')
        }),
        ('Requirements', {
            'fields': (
                'required_frameworks', 'required_categories',
                'compliance_standards', 'applicable_sectors'
            )
        }),
        ('Properties', {
            'fields': (
                'is_framework_official', 'requires_verification',
                'status', 'version'
            )
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def sections_count(self, obj):
        """Display number of sections"""
        count = obj.sections.count()
        if count > 0:
            url = reverse('admin:reports_reportsection_changelist') + f'?template__id__exact={obj.id}'
            return format_html('<a href="{}">{} sections</a>', url, count)
        return '0 sections'
    sections_count.short_description = 'Sections'


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    """Generated report admin interface"""
    list_display = [
        'name', 'company', 'template_type', 'format', 'status',
        'progress_percentage', 'file_size_mb', 'generated_by', 'created_at'
    ]
    list_filter = [
        'status', 'format', 'template__report_type',
        'is_shared', 'created_at', 'completed_at'
    ]
    search_fields = ['name', 'description', 'company__name', 'generated_by__full_name']
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'file_size_mb', 'is_expired', 'generation_time_seconds',
        'created_at', 'updated_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Report Information', {
            'fields': ('company', 'template', 'name', 'description', 'format')
        }),
        ('Generation Parameters', {
            'fields': ('period_start', 'period_end', 'parameters')
        }),
        ('Status', {
            'fields': (
                'status', 'progress_percentage', 'error_message',
                'generated_by', 'generation_time_seconds'
            )
        }),
        ('File Information', {
            'fields': ('file', 'file_size_mb')
        }),
        ('Sharing', {
            'fields': (
                'is_shared', 'shared_with', 'access_token', 'expires_at'
            ),
            'classes': ('collapse',)
        }),
        ('Data Context', {
            'fields': ('data_completeness',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'is_expired', 'created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'template', 'generated_by'
        )
    
    def template_type(self, obj):
        """Display template type"""
        return obj.template.get_report_type_display()
    template_type.short_description = 'Template Type'
    
    def file_size_mb(self, obj):
        """Display file size in MB"""
        if obj.file_size:
            return f"{obj.file_size_mb:.2f} MB"
        return '-'
    file_size_mb.short_description = 'File Size'


@admin.register(ReportSection)
class ReportSectionAdmin(admin.ModelAdmin):
    """Report section admin interface"""
    list_display = [
        'title', 'template', 'section_type', 'order',
        'is_required', 'is_active'
    ]
    list_filter = ['section_type', 'is_required', 'is_active', 'template__report_type']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'title', 'description', 'template__display_name']
    ordering = ['template', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('template', 'name', 'title', 'description', 'section_type')
        }),
        ('Configuration', {
            'fields': ('layout_config', 'required_data')
        }),
        ('Properties', {
            'fields': ('order', 'is_required', 'is_active')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('template')


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    """Report schedule admin interface"""
    list_display = [
        'name', 'company', 'template', 'frequency',
        'is_active', 'next_run', 'last_run', 'created_by'
    ]
    list_filter = ['frequency', 'is_active', 'next_run', 'created_at']
    search_fields = ['name', 'company__name', 'template__display_name']
    ordering = ['next_run']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Schedule Information', {
            'fields': ('company', 'template', 'name', 'frequency')
        }),
        ('Recipients', {
            'fields': ('recipients',)
        }),
        ('Schedule Status', {
            'fields': ('is_active', 'next_run', 'last_run')
        }),
        ('Parameters', {
            'fields': ('parameters',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'template', 'created_by'
        )


@admin.register(ReportAccess)
class ReportAccessAdmin(admin.ModelAdmin):
    """Report access admin interface"""
    list_display = [
        'report_name', 'access_type', 'accessed_by_display',
        'ip_address', 'accessed_at'
    ]
    list_filter = ['access_type', 'accessed_at']
    search_fields = [
        'report__name', 'accessed_by__full_name', 'ip_address'
    ]
    ordering = ['-accessed_at']
    readonly_fields = ['accessed_at']
    
    fieldsets = (
        ('Access Information', {
            'fields': ('report', 'accessed_by', 'access_type')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamp', {
            'fields': ('accessed_at',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'report', 'accessed_by'
        )
    
    def report_name(self, obj):
        """Display report name with link"""
        url = reverse('admin:reports_generatedreport_change', args=[obj.report.id])
        return format_html('<a href="{}">{}</a>', url, obj.report.name)
    report_name.short_description = 'Report'
    
    def accessed_by_display(self, obj):
        """Display accessed by user or anonymous"""
        if obj.accessed_by:
            return obj.accessed_by.full_name
        return 'Anonymous'
    accessed_by_display.short_description = 'Accessed By'