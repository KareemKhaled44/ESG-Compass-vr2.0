from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta, date
from .models import DashboardMetric, DashboardWidget, DashboardAlert, BenchmarkData, AnalyticsEvent


class DashboardMetricSerializer(serializers.ModelSerializer):
    """Serializer for dashboard metrics"""
    
    class Meta:
        model = DashboardMetric
        fields = [
            'id', 'metric_type', 'metric_name', 'metric_value',
            'period_start', 'period_end', 'calculated_at', 'is_current', 'version'
        ]
        read_only_fields = ['calculated_at']


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for dashboard widgets"""
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'widget_type', 'title', 'description',
            'position_x', 'position_y', 'width', 'height',
            'settings', 'is_visible', 'visible_to_roles',
            'refresh_interval_minutes', 'last_refreshed'
        ]
        read_only_fields = ['last_refreshed']


class DashboardAlertSerializer(serializers.ModelSerializer):
    """Serializer for dashboard alerts"""
    is_expired = serializers.BooleanField(read_only=True)
    read_by_name = serializers.CharField(source='read_by.full_name', read_only=True)
    
    class Meta:
        model = DashboardAlert
        fields = [
            'id', 'alert_type', 'title', 'message', 'severity',
            'is_active', 'is_read', 'read_by_name', 'read_at',
            'action_required', 'action_url', 'action_text',
            'created_at', 'expires_at', 'is_expired'
        ]
        read_only_fields = ['created_at', 'is_expired', 'read_at']


class BenchmarkDataSerializer(serializers.ModelSerializer):
    """Serializer for benchmark data"""
    
    class Meta:
        model = BenchmarkData
        fields = [
            'id', 'sector', 'region', 'benchmark_name',
            'environmental_average', 'social_average', 'governance_average',
            'overall_average', 'sample_size', 'percentile_25',
            'percentile_50', 'percentile_75', 'data_source',
            'data_period', 'is_current', 'updated_at'
        ]


class DashboardOverviewSerializer(serializers.Serializer):
    """
    Main dashboard overview serializer matching dash.html
    """
    # Key metrics (matching the 4 cards in dash.html)
    overall_esg_score = serializers.FloatField()
    environmental_score = serializers.FloatField()
    social_score = serializers.FloatField()
    governance_score = serializers.FloatField()
    
    # Score changes from last period
    overall_change = serializers.FloatField()
    environmental_change = serializers.FloatField()
    social_change = serializers.FloatField()
    governance_change = serializers.FloatField()
    
    # Progress indicators
    data_completion_percentage = serializers.FloatField()
    evidence_completion_percentage = serializers.FloatField()
    tasks_completed = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    
    # Real extracted data metrics
    extracted_metrics = serializers.DictField(required=False)
    
    # Chart data for trends (12 months)
    esg_trends = serializers.DictField()
    emissions_breakdown = serializers.DictField()
    
    # Recent activity
    recent_activity = serializers.ListField()
    
    # Recommendations
    priority_recommendations = serializers.ListField()
    
    # Targets progress
    targets_progress = serializers.DictField()


class ESGTrendsSerializer(serializers.Serializer):
    """Serializer for ESG trends chart data"""
    environmental = serializers.ListField(child=serializers.FloatField())
    social = serializers.ListField(child=serializers.FloatField())
    governance = serializers.ListField(child=serializers.FloatField())
    months = serializers.ListField(child=serializers.CharField())


class EmissionsBreakdownSerializer(serializers.Serializer):
    """Serializer for emissions breakdown chart"""
    electricity = serializers.FloatField()
    transportation = serializers.FloatField()
    waste = serializers.FloatField()
    other = serializers.FloatField()


class RecentActivitySerializer(serializers.Serializer):
    """Serializer for recent activity items"""
    type = serializers.CharField()
    message = serializers.CharField()
    time = serializers.CharField()
    icon = serializers.CharField()
    user = serializers.CharField(required=False)


class RecommendationSerializer(serializers.Serializer):
    """Serializer for ESG recommendations"""
    title = serializers.CharField()
    description = serializers.CharField()
    impact = serializers.CharField()  # High, Medium, Low
    category = serializers.CharField()  # environmental, social, governance
    priority = serializers.IntegerField()
    estimated_cost = serializers.CharField(required=False)
    time_to_implement = serializers.CharField(required=False)


class TargetProgressSerializer(serializers.Serializer):
    """Serializer for target progress tracking"""
    carbon_neutral_progress = serializers.FloatField()
    employee_satisfaction = serializers.FloatField()
    governance_compliance = serializers.FloatField()
    renewable_energy = serializers.FloatField(required=False)
    waste_reduction = serializers.FloatField(required=False)


class CompanyComparisonSerializer(serializers.Serializer):
    """
    Serializer for company performance comparison with benchmarks
    """
    company_scores = serializers.DictField()
    industry_averages = serializers.DictField()
    percentile_ranking = serializers.DictField()
    comparison_analysis = serializers.CharField()


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for analytics events"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'event_type', 'event_data', 'user_name',
            'ip_address', 'user_agent', 'referrer', 'created_at'
        ]
        read_only_fields = ['created_at']


class DashboardConfigSerializer(serializers.Serializer):
    """
    Serializer for dashboard configuration
    """
    layout = serializers.ListField(
        child=serializers.DictField(),
        help_text='Dashboard widget layout configuration'
    )
    theme = serializers.CharField(default='default')
    refresh_interval = serializers.IntegerField(default=30)
    show_notifications = serializers.BooleanField(default=True)
    compact_mode = serializers.BooleanField(default=False)


class AlertSummarySerializer(serializers.Serializer):
    """Serializer for alert summary"""
    total_alerts = serializers.IntegerField()
    unread_alerts = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()
    alerts_by_type = serializers.DictField()
    recent_alerts = DashboardAlertSerializer(many=True)


class KPISerializer(serializers.Serializer):
    """
    Serializer for Key Performance Indicators
    """
    name = serializers.CharField()
    current_value = serializers.FloatField()
    target_value = serializers.FloatField()
    unit = serializers.CharField()
    trend = serializers.CharField()  # up, down, stable
    change_percentage = serializers.FloatField()
    category = serializers.CharField()
    last_updated = serializers.DateTimeField()


class DashboardInsightSerializer(serializers.Serializer):
    """
    Serializer for dashboard insights and analytics
    """
    # Performance insights
    performance_summary = serializers.CharField()
    key_achievements = serializers.ListField()
    areas_for_improvement = serializers.ListField()
    
    # Trend analysis
    trending_upward = serializers.ListField()
    trending_downward = serializers.ListField()
    
    # Predictive insights
    forecasted_score = serializers.FloatField()
    projected_completion_date = serializers.DateField()
    
    # Competitive analysis
    industry_position = serializers.CharField()
    peer_comparison = serializers.DictField()


class QuickStatsSerializer(serializers.Serializer):
    """
    Serializer for quick statistics widget
    """
    total_assessments = serializers.IntegerField()
    active_frameworks = serializers.IntegerField()
    completed_tasks_today = serializers.IntegerField()
    reports_generated = serializers.IntegerField()
    team_members = serializers.IntegerField()
    data_points_collected = serializers.IntegerField()
    
    # Percentage improvements
    score_improvement = serializers.FloatField()
    completion_rate = serializers.FloatField()
    
    # Time-based metrics
    average_task_completion_days = serializers.FloatField()
    last_report_generated = serializers.DateTimeField()


class PerformanceMetricsSerializer(serializers.Serializer):
    """
    Serializer for detailed performance metrics
    """
    # Current period metrics
    current_period = serializers.DictField()
    
    # Previous period for comparison
    previous_period = serializers.DictField()
    
    # Year-over-year comparison
    year_over_year = serializers.DictField()
    
    # Goal tracking
    annual_goals = serializers.DictField()
    goal_progress = serializers.DictField()
    
    # Detailed breakdowns
    category_performance = serializers.DictField()
    framework_compliance = serializers.DictField()