from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class DashboardMetric(models.Model):
    """
    Store calculated dashboard metrics for performance
    """
    METRIC_TYPES = [
        ('esg_score', 'ESG Score'),
        ('data_completion', 'Data Completion'),
        ('task_progress', 'Task Progress'),
        ('compliance_status', 'Compliance Status'),
        ('benchmark_comparison', 'Benchmark Comparison'),
        ('trend_analysis', 'Trend Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='dashboard_metrics'
    )
    
    # Metric details
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    metric_name = models.CharField(max_length=255)
    metric_value = models.JSONField()
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Calculation metadata
    calculated_at = models.DateTimeField(default=timezone.now)
    calculated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Metric properties
    is_current = models.BooleanField(default=True)
    version = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = 'Dashboard Metric'
        verbose_name_plural = 'Dashboard Metrics'
        ordering = ['-calculated_at']
        indexes = [
            models.Index(fields=['company', 'metric_type', 'is_current']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.metric_name}"


class DashboardWidget(models.Model):
    """
    Dashboard widget configurations for companies
    """
    WIDGET_TYPES = [
        ('esg_scores', 'ESG Scores'),
        ('progress_tracker', 'Progress Tracker'),
        ('recent_activity', 'Recent Activity'),
        ('upcoming_tasks', 'Upcoming Tasks'),
        ('compliance_alerts', 'Compliance Alerts'),
        ('benchmark_chart', 'Benchmark Chart'),
        ('trend_chart', 'Trend Chart'),
        ('recommendations', 'Recommendations'),
        ('quick_stats', 'Quick Statistics'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='dashboard_widgets'
    )
    
    # Widget configuration
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Layout
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=1)
    
    # Widget settings
    settings = models.JSONField(
        default=dict,
        help_text='Widget-specific configuration settings'
    )
    
    # Visibility and permissions
    is_visible = models.BooleanField(default=True)
    visible_to_roles = models.JSONField(
        default=list,
        help_text='User roles that can see this widget'
    )
    
    # Refresh settings
    refresh_interval_minutes = models.IntegerField(default=30)
    last_refreshed = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dashboard Widget'
        verbose_name_plural = 'Dashboard Widgets'
        ordering = ['position_y', 'position_x']
        unique_together = ['company', 'widget_type']
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"


class DashboardAlert(models.Model):
    """
    Dashboard alerts and notifications
    """
    ALERT_TYPES = [
        ('overdue_task', 'Overdue Task'),
        ('compliance_issue', 'Compliance Issue'),
        ('data_missing', 'Missing Data'),
        ('score_drop', 'Score Decrease'),
        ('deadline_approaching', 'Deadline Approaching'),
        ('recommendation', 'Recommendation'),
        ('system_notification', 'System Notification'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='dashboard_alerts'
    )
    
    # Alert details
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    
    # Related objects
    related_task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    related_assessment = models.ForeignKey(
        'esg_assessment.ESGAssessment',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Alert lifecycle
    is_active = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    read_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='read_alerts'
    )
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Action tracking
    action_required = models.BooleanField(default=False)
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Dashboard Alert'
        verbose_name_plural = 'Dashboard Alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'is_active', 'is_read']),
            models.Index(fields=['severity', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"
    
    @property
    def is_expired(self):
        """Check if alert has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def mark_read(self, user):
        """Mark alert as read"""
        self.is_read = True
        self.read_by = user
        self.read_at = timezone.now()
        self.save()


class BenchmarkData(models.Model):
    """
    Store benchmark data for industry comparisons
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Benchmark details
    sector = models.CharField(max_length=50)
    region = models.CharField(max_length=100, default='UAE')
    benchmark_name = models.CharField(max_length=255)
    
    # Benchmark values
    environmental_average = models.FloatField()
    social_average = models.FloatField()
    governance_average = models.FloatField()
    overall_average = models.FloatField()
    
    # Statistical data
    sample_size = models.IntegerField()
    percentile_25 = models.FloatField()
    percentile_50 = models.FloatField()  # Median
    percentile_75 = models.FloatField()
    
    # Data metadata
    data_source = models.CharField(max_length=255)
    data_period = models.CharField(max_length=100)
    is_current = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Benchmark Data'
        verbose_name_plural = 'Benchmark Data'
        ordering = ['-updated_at']
        unique_together = ['sector', 'region', 'benchmark_name']
    
    def __str__(self):
        return f"{self.sector} - {self.region} - {self.benchmark_name}"


class AnalyticsEvent(models.Model):
    """
    Track user interactions and system events for analytics
    """
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('task_completed', 'Task Completed'),
        ('report_generated', 'Report Generated'),
        ('data_updated', 'Data Updated'),
        ('assessment_completed', 'Assessment Completed'),
        ('user_login', 'User Login'),
        ('export_download', 'Export Download'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='analytics_events'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Event details
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Analytics Event'
        verbose_name_plural = 'Analytics Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        user_name = self.user.full_name if self.user else 'Anonymous'
        return f"{self.company.name} - {self.event_type} by {user_name}"