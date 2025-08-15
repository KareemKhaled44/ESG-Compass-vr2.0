from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class ReportTemplate(models.Model):
    """
    Report templates for different ESG frameworks and purposes
    Matches the report types shown in report.html
    """
    REPORT_TYPES = [
        ('esg_comprehensive', 'ESG Comprehensive Report'),
        ('dst_compliance', 'Dubai Sustainable Tourism'),
        ('green_key', 'Green Key Certification'),
        ('custom_export', 'Custom Export'),
        ('quarterly_summary', 'Quarterly Summary'),
        ('compliance_tracker', 'UAE Compliance Tracker'),
        ('annual_report', 'Annual ESG Report'),
        ('benchmark_analysis', 'Benchmark Analysis'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('xml', 'XML'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    description = models.TextField()
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    
    # Template configuration
    template_config = models.JSONField(
        default=dict,
        help_text='Template configuration and layout settings'
    )
    
    # Data requirements
    required_frameworks = models.JSONField(
        default=list,
        help_text='Required ESG frameworks for this report'
    )
    required_categories = models.JSONField(
        default=list,
        help_text='Required ESG categories (environmental, social, governance)'
    )
    
    # Output formats
    supported_formats = models.JSONField(
        default=list,
        help_text='Supported output formats'
    )
    
    # Compliance and certification
    compliance_standards = models.JSONField(
        default=list,
        help_text='Compliance standards this report addresses'
    )
    
    # Applicability
    applicable_sectors = models.JSONField(
        default=list,
        help_text='Business sectors this template applies to'
    )
    
    # Template properties
    is_framework_official = models.BooleanField(
        default=False,
        help_text='Is this an official framework template?'
    )
    requires_verification = models.BooleanField(
        default=False,
        help_text='Does this report require third-party verification?'
    )
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    version = models.CharField(max_length=50, default='1.0')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Report Template'
        verbose_name_plural = 'Report Templates'
        ordering = ['report_type', 'name']
    
    def __str__(self):
        return self.display_name
    
    def get_icon_class(self):
        """Get Font Awesome icon class for report type"""
        icons = {
            'esg_comprehensive': 'fa-solid fa-chart-pie',
            'dst_compliance': 'fa-solid fa-building',
            'green_key': 'fa-solid fa-key',
            'custom_export': 'fa-solid fa-file-export',
            'quarterly_summary': 'fa-solid fa-calendar-check',
            'compliance_tracker': 'fa-solid fa-shield-check',
            'annual_report': 'fa-solid fa-file-alt',
            'benchmark_analysis': 'fa-solid fa-chart-bar',
        }
        return icons.get(self.report_type, 'fa-solid fa-file')
    
    def get_color_class(self):
        """Get color class for report type"""
        colors = {
            'esg_comprehensive': 'from-brand-green to-brand-teal',
            'dst_compliance': 'from-brand-blue to-brand-teal',
            'green_key': 'from-brand-green to-brand-blue',
            'custom_export': 'from-purple-500 to-brand-teal',
            'quarterly_summary': 'from-brand-teal to-brand-green',
            'compliance_tracker': 'from-red-500 to-brand-blue',
        }
        return colors.get(self.report_type, 'from-gray-500 to-gray-700')


class GeneratedReport(models.Model):
    """
    Track generated reports for companies
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='generated_reports'
    )
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='generated_reports'
    )
    
    # Report details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    format = models.CharField(max_length=10, choices=ReportTemplate.FORMAT_CHOICES)
    
    # Generation parameters
    period_start = models.DateField()
    period_end = models.DateField()
    parameters = models.JSONField(
        default=dict,
        help_text='Report generation parameters and filters'
    )
    
    # Status and progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress_percentage = models.FloatField(default=0.0)
    error_message = models.TextField(blank=True)
    
    # File information
    file = models.FileField(upload_to='generated_reports/', null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Generation metadata
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_reports'
    )
    generation_time_seconds = models.FloatField(null=True, blank=True)
    
    # Data completeness at time of generation
    data_completeness = models.JSONField(
        default=dict,
        help_text='Data completeness metrics at generation time'
    )
    
    # Sharing and access
    is_shared = models.BooleanField(default=False)
    shared_with = models.JSONField(
        default=list,
        help_text='List of user IDs or email addresses shared with'
    )
    access_token = models.CharField(max_length=255, blank=True, unique=True)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Generated Report'
        verbose_name_plural = 'Generated Reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['template', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"
    
    @property
    def is_expired(self):
        """Check if report has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return self.file_size / (1024 * 1024)
        return 0
    
    def mark_completed(self, file_path=None):
        """Mark report as completed"""
        self.status = 'completed'
        self.progress_percentage = 100.0
        self.completed_at = timezone.now()
        if file_path:
            self.file = file_path
        self.save()
    
    def mark_failed(self, error_message):
        """Mark report as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.save()


class ReportSection(models.Model):
    """
    Configurable sections for report templates
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    
    # Section details
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Section configuration
    section_type = models.CharField(max_length=50, choices=[
        ('cover', 'Cover Page'),
        ('executive_summary', 'Executive Summary'),
        ('methodology', 'Methodology'),
        ('environmental', 'Environmental Metrics'),
        ('social', 'Social Metrics'),
        ('governance', 'Governance Metrics'),
        ('compliance', 'Compliance Status'),
        ('recommendations', 'Recommendations'),
        ('appendix', 'Appendix'),
        ('custom', 'Custom Section'),
    ])
    
    # Layout and styling
    layout_config = models.JSONField(
        default=dict,
        help_text='Section layout and styling configuration'
    )
    
    # Data requirements
    required_data = models.JSONField(
        default=list,
        help_text='Required data fields for this section'
    )
    
    # Section properties
    order = models.IntegerField(default=0)
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Report Section'
        verbose_name_plural = 'Report Sections'
        ordering = ['template', 'order']
        unique_together = ['template', 'name']
    
    def __str__(self):
        return f"{self.template.name} - {self.title}"


class ReportSchedule(models.Model):
    """
    Scheduled automatic report generation
    """
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='report_schedules'
    )
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    # Schedule details
    name = models.CharField(max_length=255)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    
    # Recipients
    recipients = models.JSONField(
        default=list,
        help_text='List of email addresses to send reports to'
    )
    
    # Schedule configuration
    is_active = models.BooleanField(default=True)
    next_run = models.DateTimeField()
    last_run = models.DateTimeField(null=True, blank=True)
    
    # Generation parameters
    parameters = models.JSONField(
        default=dict,
        help_text='Default parameters for scheduled generation'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Report Schedule'
        verbose_name_plural = 'Report Schedules'
        ordering = ['company', 'name']
    
    def __str__(self):
        return f"{self.company.name} - {self.name} ({self.frequency})"


class ReportAccess(models.Model):
    """
    Track report access and downloads
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        GeneratedReport,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    
    # Access details
    accessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Access type
    access_type = models.CharField(max_length=20, choices=[
        ('view', 'Viewed'),
        ('download', 'Downloaded'),
        ('share', 'Shared'),
    ])
    
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Report Access'
        verbose_name_plural = 'Report Access Logs'
        ordering = ['-accessed_at']
    
    def __str__(self):
        user = self.accessed_by.full_name if self.accessed_by else 'Anonymous'
        return f"{self.report.name} {self.access_type} by {user}"