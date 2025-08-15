from rest_framework import serializers
from django.utils import timezone
from .models import ReportTemplate, GeneratedReport, ReportSection, ReportSchedule, ReportAccess


class ReportSectionSerializer(serializers.ModelSerializer):
    """Serializer for report sections"""
    
    class Meta:
        model = ReportSection
        fields = [
            'id', 'name', 'title', 'description', 'section_type',
            'layout_config', 'required_data', 'order', 'is_required', 'is_active'
        ]


class ReportTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for report templates
    Matches the report tiles shown in report.html
    """
    sections = ReportSectionSerializer(many=True, read_only=True)
    icon_class = serializers.CharField(source='get_icon_class', read_only=True)
    color_class = serializers.CharField(source='get_color_class', read_only=True)
    
    # Status indicators matching report.html
    readiness_status = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'display_name', 'description', 'report_type',
            'template_config', 'required_frameworks', 'required_categories',
            'supported_formats', 'compliance_standards', 'applicable_sectors',
            'is_framework_official', 'requires_verification', 'status', 'version',
            'sections', 'icon_class', 'color_class', 'readiness_status',
            'completion_percentage', 'status_color', 'status_text'
        ]
    
    def get_readiness_status(self, obj):
        """Get readiness status based on data availability"""
        # In a real implementation, this would check actual data completeness
        # For now, return status matching report.html examples
        status_map = {
            'esg_comprehensive': 'ready',
            'dst_compliance': 'ready', 
            'green_key': 'pending',
            'custom_export': 'ready',
            'quarterly_summary': 'ready',
            'compliance_tracker': 'urgent',
        }
        return status_map.get(obj.report_type, 'ready')
    
    def get_completion_percentage(self, obj):
        """Get data completion percentage for this report type"""
        # Mock data matching report.html
        percentages = {
            'esg_comprehensive': 94.0,
            'dst_compliance': 87.0,
            'green_key': 73.0,
            'custom_export': 100.0,
            'quarterly_summary': 100.0,
            'compliance_tracker': 68.0,
        }
        return percentages.get(obj.report_type, 90.0)
    
    def get_status_color(self, obj):
        """Get status color class"""
        status = self.get_readiness_status(obj)
        colors = {
            'ready': 'brand-green',
            'pending': 'yellow-500',
            'urgent': 'red-500'
        }
        return colors.get(status, 'brand-green')
    
    def get_status_text(self, obj):
        """Get status text"""
        status = self.get_readiness_status(obj)
        texts = {
            'ready': 'READY',
            'pending': 'PENDING',
            'urgent': 'URGENT'
        }
        return texts.get(status, 'READY')


class GeneratedReportSerializer(serializers.ModelSerializer):
    """Serializer for generated reports"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    template_name = serializers.CharField(source='template.display_name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.full_name', read_only=True)
    file_size_mb = serializers.FloatField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    # Add template information for frontend
    template = ReportTemplateSerializer(read_only=True)
    report_type = serializers.CharField(source='template.report_type', read_only=True)
    report_period = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'name', 'description', 'format', 'period_start', 'period_end',
            'status', 'progress_percentage', 'error_message', 'file', 'file_size_mb',
            'is_expired', 'is_shared', 'expires_at', 'company_name', 'template_name',
            'generated_by_name', 'generation_time_seconds', 'data_completeness',
            'created_at', 'updated_at', 'completed_at',
            # Frontend required fields
            'template', 'report_type', 'report_period'
        ]
        read_only_fields = [
            'status', 'progress_percentage', 'file_size_mb', 'is_expired',
            'generation_time_seconds', 'created_at', 'updated_at', 'completed_at'
        ]
    
    def get_report_period(self, obj):
        """Format report period for frontend display"""
        if obj.period_start and obj.period_end:
            start = obj.period_start.strftime('%b %Y')
            end = obj.period_end.strftime('%b %Y')
            if start == end:
                return start
            else:
                return f"{start} - {end}"
        return None


class ReportGenerationRequestSerializer(serializers.Serializer):
    """
    Serializer for report generation requests
    """
    template_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    format = serializers.ChoiceField(
        choices=ReportTemplate.FORMAT_CHOICES,
        default='pdf'
    )
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    parameters = serializers.DictField(required=False, default=dict)
    
    def validate(self, attrs):
        """Validate date range"""
        if attrs['period_start'] >= attrs['period_end']:
            raise serializers.ValidationError(
                "Period start date must be before end date"
            )
        
        if attrs['period_end'] > timezone.now().date():
            raise serializers.ValidationError(
                "Period end date cannot be in the future"
            )
        
        return attrs


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializer for report schedules"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    template_name = serializers.CharField(source='template.display_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'name', 'frequency', 'recipients', 'is_active',
            'next_run', 'last_run', 'parameters', 'company_name',
            'template_name', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['last_run', 'created_at', 'updated_at']


class ReportDashboardSerializer(serializers.Serializer):
    """
    Serializer for report dashboard data (report.html)
    """
    # Available templates with status
    available_templates = ReportTemplateSerializer(many=True)
    
    # Recent reports
    recent_reports = GeneratedReportSerializer(many=True)
    
    # Statistics
    total_reports_generated = serializers.IntegerField()
    reports_this_month = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    
    # Quick actions
    can_generate_dst = serializers.BooleanField()
    can_generate_green_key = serializers.BooleanField()
    data_completeness_overall = serializers.FloatField()


class ComplianceStatusSerializer(serializers.Serializer):
    """
    Serializer for compliance status (matching report.html compliance tracker)
    """
    framework = serializers.CharField()
    compliance_percentage = serializers.FloatField()
    status = serializers.CharField()  # compliant, partial, non_compliant
    missing_requirements = serializers.ListField()
    last_updated = serializers.DateTimeField()
    next_review_date = serializers.DateField()


class ReportAccessSerializer(serializers.ModelSerializer):
    """Serializer for report access logs"""
    accessed_by_name = serializers.CharField(
        source='accessed_by.full_name', 
        read_only=True
    )
    report_name = serializers.CharField(source='report.name', read_only=True)
    
    class Meta:
        model = ReportAccess
        fields = [
            'id', 'access_type', 'ip_address', 'user_agent',
            'accessed_by_name', 'report_name', 'accessed_at'
        ]
        read_only_fields = ['accessed_at']


class ReportShareSerializer(serializers.Serializer):
    """Serializer for sharing reports"""
    email_addresses = serializers.ListField(
        child=serializers.EmailField()
    )
    message = serializers.CharField(required=False, allow_blank=True)
    expires_in_days = serializers.IntegerField(
        default=30,
        min_value=1,
        max_value=365
    )
    allow_download = serializers.BooleanField(default=True)


class CustomReportConfigSerializer(serializers.Serializer):
    """
    Serializer for custom report configuration
    """
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    
    # Data selection
    include_categories = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            ('environmental', 'Environmental'),
            ('social', 'Social'), 
            ('governance', 'Governance')
        ]),
        default=['environmental', 'social', 'governance']
    )
    
    # Framework selection
    include_frameworks = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    
    # Time period
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    
    # Output format
    format = serializers.ChoiceField(
        choices=ReportTemplate.FORMAT_CHOICES,
        default='pdf'
    )
    
    # Content options
    include_charts = serializers.BooleanField(default=True)
    include_recommendations = serializers.BooleanField(default=True)
    include_benchmarks = serializers.BooleanField(default=False)
    include_evidence = serializers.BooleanField(default=False)
    
    # Styling options
    company_branding = serializers.BooleanField(default=True)
    confidential_watermark = serializers.BooleanField(default=False)