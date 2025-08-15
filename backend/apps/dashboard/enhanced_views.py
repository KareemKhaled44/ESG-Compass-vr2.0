"""
Enhanced Dashboard and Report Views that use extracted file data
Replaces the original views to properly fetch data from uploaded files
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q, Max, Min
from django.core.cache import cache
from datetime import timedelta, datetime
import logging

from apps.tasks.models import Task, TaskAttachment
from apps.companies.models import Company
from apps.dashboard.models import DashboardMetric
from apps.reports.models import GeneratedReport
from apps.files.models import ExtractedFileData, update_company_metrics_cache

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def enhanced_dashboard_overview(request):
    """
    Enhanced dashboard that uses extracted file data
    Replaces the original dashboard_overview view
    """
    company = request.user.company
    if not company:
        return Response(
            {'error': 'User not associated with a company'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or update cached metrics
    cache_key = f"company_metrics_{company.id}"
    cached_metrics = cache.get(cache_key)
    
    if not cached_metrics:
        cached_metrics = update_company_metrics_cache(company)
    
    # Get extracted data
    extracted_data = ExtractedFileData.objects.filter(
        task_attachment__task__company=company,
        processing_status='completed'
    )
    
    # Calculate ESG scores based on actual data
    scores = calculate_esg_scores_from_extracted_data(company, extracted_data)
    
    # Get latest environmental metrics
    env_metrics = get_latest_environmental_metrics(extracted_data)
    
    # Get latest social metrics
    social_metrics = get_latest_social_metrics(extracted_data)
    
    # Get latest governance metrics
    gov_metrics = get_latest_governance_metrics(extracted_data)
    
    # Calculate trends from historical data
    trends = calculate_trends_from_extracted_data(company, extracted_data)
    
    # Get task progress
    task_stats = get_task_statistics(company)
    
    # Build dashboard response
    dashboard_data = {
        # ESG Scores
        'overall_esg_score': scores['overall'],
        'environmental_score': scores['environmental'],
        'social_score': scores['social'],
        'governance_score': scores['governance'],
        
        # Score changes (calculated from trends)
        'overall_change': trends['overall_change'],
        'environmental_change': trends['environmental_change'],
        'social_change': trends['social_change'],
        'governance_change': trends['governance_change'],
        
        # Data completeness
        'data_completion_percentage': scores['data_completion'],
        'evidence_completion_percentage': scores['evidence_completion'],
        
        # Task progress
        'tasks_completed': task_stats['completed'],
        'total_tasks': task_stats['total'],
        
        # Environmental metrics from files
        'environmental_metrics': env_metrics,
        
        # Social metrics from files
        'social_metrics': social_metrics,
        
        # Governance metrics from files
        'governance_metrics': gov_metrics,
        
        # Trends
        'esg_trends': trends['monthly_trends'],
        
        # Emissions breakdown (from latest data)
        'emissions_breakdown': calculate_emissions_breakdown(env_metrics),
        
        # Recent activity
        'recent_activity': get_recent_file_activity(company),
        
        # Data quality indicators
        'data_quality': {
            'total_files_processed': cached_metrics.get('total_files_processed', 0),
            'average_confidence': cached_metrics.get('average_confidence', 0),
            'last_update': cached_metrics.get('last_updated', timezone.now().isoformat()),
        },
        
        # Recommendations based on data gaps
        'priority_recommendations': generate_data_driven_recommendations(
            company, extracted_data, env_metrics, social_metrics, gov_metrics
        ),
        
        # Target progress (calculated from actual data)
        'targets_progress': calculate_target_progress(env_metrics, social_metrics, gov_metrics),
    }
    
    return Response(dashboard_data)


def calculate_esg_scores_from_extracted_data(company, extracted_data):
    """
    Calculate ESG scores based on extracted file data
    """
    scores = {
        'overall': 50.0,
        'environmental': 50.0,
        'social': 50.0,
        'governance': 50.0,
        'data_completion': 0.0,
        'evidence_completion': 0.0,
    }
    
    # Environmental score based on data availability and values
    env_data_points = 0
    env_score_boost = 0
    
    # Check for energy data
    if extracted_data.exclude(energy_consumption_kwh__isnull=True).exists():
        env_data_points += 1
        # Check for improvement (compare latest vs oldest)
        energy_trend = extracted_data.exclude(
            energy_consumption_kwh__isnull=True
        ).order_by('extraction_date')
        if energy_trend.count() > 1:
            first = energy_trend.first().energy_consumption_kwh
            last = energy_trend.last().energy_consumption_kwh
            if last < first:  # Reduction is good
                env_score_boost += 10
    
    # Check for water data
    if extracted_data.exclude(water_usage_liters__isnull=True).exists():
        env_data_points += 1
        water_trend = extracted_data.exclude(
            water_usage_liters__isnull=True
        ).order_by('extraction_date')
        if water_trend.count() > 1:
            first = water_trend.first().water_usage_liters
            last = water_trend.last().water_usage_liters
            if last < first:
                env_score_boost += 10
    
    # Check for waste data
    if extracted_data.exclude(waste_generated_kg__isnull=True).exists():
        env_data_points += 1
        waste_trend = extracted_data.exclude(
            waste_generated_kg__isnull=True
        ).order_by('extraction_date')
        if waste_trend.count() > 1:
            first = waste_trend.first().waste_generated_kg
            last = waste_trend.last().waste_generated_kg
            if last < first:
                env_score_boost += 10
    
    # Check for carbon data
    if extracted_data.exclude(carbon_emissions_tco2__isnull=True).exists():
        env_data_points += 1
        carbon_trend = extracted_data.exclude(
            carbon_emissions_tco2__isnull=True
        ).order_by('extraction_date')
        if carbon_trend.count() > 1:
            first = carbon_trend.first().carbon_emissions_tco2
            last = carbon_trend.last().carbon_emissions_tco2
            if last < first:
                env_score_boost += 10
    
    # Calculate environmental score
    if env_data_points > 0:
        scores['environmental'] = min(50 + (env_data_points * 10) + env_score_boost, 95)
    
    # Social score based on data
    social_data_points = 0
    social_score_boost = 0
    
    if extracted_data.exclude(total_employees__isnull=True).exists():
        social_data_points += 1
    
    if extracted_data.exclude(training_hours__isnull=True).exists():
        social_data_points += 1
        # Higher training hours is better
        avg_training = extracted_data.exclude(
            training_hours__isnull=True
        ).aggregate(avg=Avg('training_hours'))['avg']
        if avg_training and avg_training > 20:
            social_score_boost += 10
    
    if extracted_data.exclude(safety_incidents__isnull=True).exists():
        social_data_points += 1
        # Lower incidents is better
        latest_incidents = extracted_data.exclude(
            safety_incidents__isnull=True
        ).order_by('-extraction_date').first()
        if latest_incidents and latest_incidents.safety_incidents == 0:
            social_score_boost += 15
    
    if extracted_data.exclude(employee_satisfaction_score__isnull=True).exists():
        social_data_points += 1
        latest_satisfaction = extracted_data.exclude(
            employee_satisfaction_score__isnull=True
        ).order_by('-extraction_date').first()
        if latest_satisfaction and latest_satisfaction.employee_satisfaction_score > 80:
            social_score_boost += 10
    
    if social_data_points > 0:
        scores['social'] = min(50 + (social_data_points * 10) + social_score_boost, 95)
    
    # Governance score
    gov_data_points = 0
    gov_score_boost = 0
    
    if extracted_data.exclude(compliance_score__isnull=True).exists():
        gov_data_points += 1
        latest_compliance = extracted_data.exclude(
            compliance_score__isnull=True
        ).order_by('-extraction_date').first()
        if latest_compliance and latest_compliance.compliance_score > 85:
            gov_score_boost += 20
    
    if extracted_data.exclude(board_meetings__isnull=True).exists():
        gov_data_points += 1
        latest_meetings = extracted_data.exclude(
            board_meetings__isnull=True
        ).order_by('-extraction_date').first()
        if latest_meetings and latest_meetings.board_meetings >= 12:
            gov_score_boost += 10
    
    if gov_data_points > 0:
        scores['governance'] = min(50 + (gov_data_points * 15) + gov_score_boost, 95)
    
    # Overall score
    scores['overall'] = (scores['environmental'] + scores['social'] + scores['governance']) / 3
    
    # Data completion based on files processed
    total_tasks = Task.objects.filter(company=company).count()
    files_with_data = extracted_data.count()
    
    if total_tasks > 0:
        scores['evidence_completion'] = min((files_with_data / total_tasks) * 100, 100)
    
    # Data completion based on confidence
    if files_with_data > 0:
        avg_confidence = extracted_data.aggregate(avg=Avg('confidence_score'))['avg'] or 0
        scores['data_completion'] = avg_confidence
    
    return scores


def get_latest_environmental_metrics(extracted_data):
    """
    Get the latest environmental metrics from extracted data
    """
    metrics = {}
    
    # Energy consumption
    energy_record = extracted_data.exclude(
        energy_consumption_kwh__isnull=True
    ).order_by('-extraction_date').first()
    
    if energy_record:
        metrics['energy_consumption'] = {
            'current_kwh': energy_record.energy_consumption_kwh,
            'source_file': energy_record.task_attachment.original_filename,
            'extraction_date': energy_record.extraction_date.isoformat(),
            'confidence': energy_record.confidence_score,
            # Calculate change if we have historical data
            'previous_kwh': None,
            'reduction_percentage': 0,
        }
        
        # Get previous record for comparison
        previous = extracted_data.exclude(
            energy_consumption_kwh__isnull=True
        ).exclude(
            id=energy_record.id
        ).order_by('-extraction_date').first()
        
        if previous:
            metrics['energy_consumption']['previous_kwh'] = previous.energy_consumption_kwh
            if previous.energy_consumption_kwh > 0:
                reduction = ((previous.energy_consumption_kwh - energy_record.energy_consumption_kwh) 
                           / previous.energy_consumption_kwh) * 100
                metrics['energy_consumption']['reduction_percentage'] = round(reduction, 1)
    
    # Water usage
    water_record = extracted_data.exclude(
        water_usage_liters__isnull=True
    ).order_by('-extraction_date').first()
    
    if water_record:
        metrics['water_usage'] = {
            'current_liters': water_record.water_usage_liters,
            'source_file': water_record.task_attachment.original_filename,
            'extraction_date': water_record.extraction_date.isoformat(),
            'confidence': water_record.confidence_score,
        }
    
    # Waste management
    waste_record = extracted_data.exclude(
        waste_generated_kg__isnull=True
    ).order_by('-extraction_date').first()
    
    if waste_record:
        metrics['waste_management'] = {
            'total_waste_kg': waste_record.waste_generated_kg,
            'source_file': waste_record.task_attachment.original_filename,
            'extraction_date': waste_record.extraction_date.isoformat(),
            'confidence': waste_record.confidence_score,
        }
    
    # Carbon emissions
    carbon_record = extracted_data.exclude(
        carbon_emissions_tco2__isnull=True
    ).order_by('-extraction_date').first()
    
    if carbon_record:
        metrics['carbon_emissions'] = {
            'total_tco2': carbon_record.carbon_emissions_tco2,
            'source_file': carbon_record.task_attachment.original_filename,
            'extraction_date': carbon_record.extraction_date.isoformat(),
            'confidence': carbon_record.confidence_score,
        }
    
    # Renewable energy
    renewable_record = extracted_data.exclude(
        renewable_energy_percentage__isnull=True
    ).order_by('-extraction_date').first()
    
    if renewable_record:
        metrics['renewable_energy'] = {
            'percentage': renewable_record.renewable_energy_percentage,
            'source_file': renewable_record.task_attachment.original_filename,
            'confidence': renewable_record.confidence_score,
        }
    
    return metrics


def get_latest_social_metrics(extracted_data):
    """
    Get the latest social metrics from extracted data
    """
    metrics = {}
    
    # Employee metrics
    employee_record = extracted_data.exclude(
        total_employees__isnull=True
    ).order_by('-extraction_date').first()
    
    if employee_record:
        metrics['employee_metrics'] = {
            'total_employees': employee_record.total_employees,
            'source_file': employee_record.task_attachment.original_filename,
            'extraction_date': employee_record.extraction_date.isoformat(),
            'confidence': employee_record.confidence_score,
        }
    
    # Training hours
    training_records = extracted_data.exclude(
        training_hours__isnull=True
    )
    
    if training_records.exists():
        avg_training = training_records.aggregate(avg=Avg('training_hours'))['avg']
        latest_training = training_records.order_by('-extraction_date').first()
        
        metrics['training'] = {
            'average_hours': round(avg_training, 1) if avg_training else 0,
            'latest_hours': latest_training.training_hours,
            'source_file': latest_training.task_attachment.original_filename,
            'records_count': training_records.count(),
        }
    
    # Safety incidents
    safety_record = extracted_data.exclude(
        safety_incidents__isnull=True
    ).order_by('-extraction_date').first()
    
    if safety_record:
        metrics['health_safety'] = {
            'incidents_count': safety_record.safety_incidents,
            'source_file': safety_record.task_attachment.original_filename,
            'extraction_date': safety_record.extraction_date.isoformat(),
            'confidence': safety_record.confidence_score,
        }
    
    # Employee satisfaction
    satisfaction_record = extracted_data.exclude(
        employee_satisfaction_score__isnull=True
    ).order_by('-extraction_date').first()
    
    if satisfaction_record:
        metrics['employee_satisfaction'] = {
            'score': satisfaction_record.employee_satisfaction_score,
            'source_file': satisfaction_record.task_attachment.original_filename,
            'confidence': satisfaction_record.confidence_score,
        }
    
    return metrics


def get_latest_governance_metrics(extracted_data):
    """
    Get the latest governance metrics from extracted data
    """
    metrics = {}
    
    # Compliance score
    compliance_record = extracted_data.exclude(
        compliance_score__isnull=True
    ).order_by('-extraction_date').first()
    
    if compliance_record:
        metrics['compliance'] = {
            'score': compliance_record.compliance_score,
            'source_file': compliance_record.task_attachment.original_filename,
            'extraction_date': compliance_record.extraction_date.isoformat(),
            'confidence': compliance_record.confidence_score,
        }
    
    # Board meetings
    board_record = extracted_data.exclude(
        board_meetings__isnull=True
    ).order_by('-extraction_date').first()
    
    if board_record:
        metrics['board_structure'] = {
            'meetings_count': board_record.board_meetings,
            'source_file': board_record.task_attachment.original_filename,
            'extraction_date': board_record.extraction_date.isoformat(),
            'confidence': board_record.confidence_score,
        }
    
    return metrics


def calculate_trends_from_extracted_data(company, extracted_data):
    """
    Calculate trends from historical extracted data
    """
    trends = {
        'overall_change': 0,
        'environmental_change': 0,
        'social_change': 0,
        'governance_change': 0,
        'monthly_trends': {
            'environmental': [],
            'social': [],
            'governance': [],
            'months': []
        }
    }
    
    # Get data from last 12 months
    twelve_months_ago = timezone.now() - timedelta(days=365)
    
    # Group by month
    from django.db.models.functions import TruncMonth
    
    monthly_data = extracted_data.filter(
        extraction_date__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('extraction_date')
    ).values('month').annotate(
        avg_confidence=Avg('confidence_score'),
        count=Count('id')
    ).order_by('month')
    
    # Build monthly trend data
    for month_data in monthly_data:
        month_str = month_data['month'].strftime('%b')
        trends['monthly_trends']['months'].append(month_str)
        
        # Calculate scores for this month (simplified)
        base_score = 50
        score_boost = min(month_data['count'] * 5, 30)  # More files = better
        confidence_boost = (month_data['avg_confidence'] / 100) * 20
        
        month_score = base_score + score_boost + confidence_boost
        
        trends['monthly_trends']['environmental'].append(round(month_score, 1))
        trends['monthly_trends']['social'].append(round(month_score * 0.95, 1))
        trends['monthly_trends']['governance'].append(round(month_score * 0.9, 1))
    
    # Calculate changes (compare last month to previous month)
    if len(trends['monthly_trends']['environmental']) >= 2:
        trends['environmental_change'] = (
            trends['monthly_trends']['environmental'][-1] - 
            trends['monthly_trends']['environmental'][-2]
        )
        trends['social_change'] = (
            trends['monthly_trends']['social'][-1] - 
            trends['monthly_trends']['social'][-2]
        )
        trends['governance_change'] = (
            trends['monthly_trends']['governance'][-1] - 
            trends['monthly_trends']['governance'][-2]
        )
        trends['overall_change'] = (
            trends['environmental_change'] + 
            trends['social_change'] + 
            trends['governance_change']
        ) / 3
    
    return trends


def get_task_statistics(company):
    """
    Get task completion statistics
    """
    tasks = Task.objects.filter(company=company)
    
    return {
        'total': tasks.count(),
        'completed': tasks.filter(status='completed').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'todo': tasks.filter(status='todo').count(),
    }


def calculate_emissions_breakdown(env_metrics):
    """
    Calculate emissions breakdown from environmental metrics
    """
    breakdown = {
        'electricity': 0,
        'transportation': 0,
        'waste': 0,
        'other': 0
    }
    
    total_emissions = 0
    
    # If we have carbon data, use it
    if 'carbon_emissions' in env_metrics:
        total_emissions = env_metrics['carbon_emissions']['total_tco2']
        
        # Estimate breakdown based on typical patterns
        breakdown['electricity'] = total_emissions * 0.45
        breakdown['transportation'] = total_emissions * 0.30
        breakdown['waste'] = total_emissions * 0.15
        breakdown['other'] = total_emissions * 0.10
    
    # If we have energy data, refine electricity emissions
    if 'energy_consumption' in env_metrics:
        kwh = env_metrics['energy_consumption']['current_kwh']
        # UAE grid emission factor: ~0.4 kg CO2/kWh
        electricity_emissions = (kwh * 0.4) / 1000  # Convert to tCO2
        breakdown['electricity'] = electricity_emissions
    
    return breakdown


def get_recent_file_activity(company):
    """
    Get recent file upload and processing activity
    """
    activities = []
    
    # Get recent file uploads
    recent_files = ExtractedFileData.objects.filter(
        task_attachment__task__company=company,
        processing_status='completed'
    ).order_by('-extraction_date')[:10]
    
    for file_record in recent_files:
        # Determine activity type based on extracted metrics
        activity_type = 'upload'
        message = f"Processed {file_record.task_attachment.original_filename}"
        
        # Add specific details based on what was found
        metrics_found = []
        if file_record.energy_consumption_kwh:
            metrics_found.append('energy data')
        if file_record.water_usage_liters:
            metrics_found.append('water data')
        if file_record.carbon_emissions_tco2:
            metrics_found.append('emissions data')
        if file_record.total_employees:
            metrics_found.append('employee data')
        if file_record.compliance_score:
            metrics_found.append('compliance score')
        
        if metrics_found:
            message += f" - Found: {', '.join(metrics_found)}"
            activity_type = 'data_extracted'
        
        activities.append({
            'type': activity_type,
            'message': message,
            'time': _format_time_ago(file_record.extraction_date),
            'icon': 'file-text' if metrics_found else 'upload',
            'category': file_record.task_attachment.task.category,
            'confidence': f"{file_record.confidence_score:.0f}%"
        })
    
    return activities


def generate_data_driven_recommendations(company, extracted_data, env_metrics, social_metrics, gov_metrics):
    """
    Generate recommendations based on actual data gaps and trends
    """
    recommendations = []
    
    # Check for missing environmental data
    if not env_metrics.get('energy_consumption'):
        recommendations.append({
            'title': 'Upload Energy Consumption Data',
            'description': 'Upload utility bills or energy monitoring reports to track consumption',
            'impact': 'High',
            'category': 'environmental',
            'priority': 1,
            'action_required': 'Upload DEWA/ADDC bills or energy audit reports'
        })
    elif env_metrics.get('energy_consumption', {}).get('reduction_percentage', 0) < 5:
        recommendations.append({
            'title': 'Implement Energy Reduction Measures',
            'description': 'Energy consumption shows minimal reduction. Consider efficiency upgrades',
            'impact': 'High',
            'category': 'environmental',
            'priority': 2,
            'action_required': 'Develop and document energy efficiency plan'
        })
    
    # Check for missing water data
    if not env_metrics.get('water_usage'):
        recommendations.append({
            'title': 'Track Water Consumption',
            'description': 'Upload water bills or usage reports for tracking',
            'impact': 'Medium',
            'category': 'environmental',
            'priority': 3,
            'action_required': 'Upload water utility bills'
        })
    
    # Check for missing social data
    if not social_metrics.get('employee_metrics'):
        recommendations.append({
            'title': 'Document Employee Information',
            'description': 'Upload HR reports with employee counts and demographics',
            'impact': 'Medium',
            'category': 'social',
            'priority': 2,
            'action_required': 'Upload HR analytics report'
        })
    
    if not social_metrics.get('training'):
        recommendations.append({
            'title': 'Track Training Hours',
            'description': 'Document employee training and development programs',
            'impact': 'Medium',
            'category': 'social',
            'priority': 3,
            'action_required': 'Upload training records or LMS reports'
        })
    
    # Check for safety data
    if not social_metrics.get('health_safety'):
        recommendations.append({
            'title': 'Report Safety Metrics',
            'description': 'Upload safety incident reports and statistics',
            'impact': 'High',
            'category': 'social',
            'priority': 1,
            'action_required': 'Upload HSE reports'
        })
    
    # Check for governance data
    if not gov_metrics.get('compliance'):
        recommendations.append({
            'title': 'Document Compliance Status',
            'description': 'Upload compliance audit reports or certifications',
            'impact': 'High',
            'category': 'governance',
            'priority': 1,
            'action_required': 'Upload compliance certificates or audit reports'
        })
    
    # Check data quality
    avg_confidence = extracted_data.aggregate(avg=Avg('confidence_score'))['avg'] or 0
    if avg_confidence < 70:
        recommendations.append({
            'title': 'Improve Data Quality',
            'description': 'Upload clearer documents or structured data files (Excel, CSV) for better extraction',
            'impact': 'High',
            'category': 'general',
            'priority': 1,
            'action_required': 'Replace low-quality scans with original digital files'
        })
    
    # Sort by priority and return top 5
    recommendations.sort(key=lambda x: x['priority'])
    return recommendations[:5]


def calculate_target_progress(env_metrics, social_metrics, gov_metrics):
    """
    Calculate progress towards targets based on actual data
    """
    progress = {
        'carbon_neutral_progress': 0,
        'employee_satisfaction': 0,
        'governance_compliance': 0,
        'renewable_energy': 0,
        'waste_reduction': 0
    }
    
    # Carbon neutral progress (based on emissions reduction)
    if env_metrics.get('carbon_emissions'):
        # Assume target is 50% reduction
        current = env_metrics['carbon_emissions']['total_tco2']
        # This is simplified - in reality you'd compare to baseline
        progress['carbon_neutral_progress'] = max(0, min(100, (1000 - current) / 10))
    
    # Employee satisfaction
    if social_metrics.get('employee_satisfaction'):
        score = social_metrics['employee_satisfaction']['score']
        # Target is 100%
        progress['employee_satisfaction'] = score
    
    # Governance compliance
    if gov_metrics.get('compliance'):
        progress['governance_compliance'] = gov_metrics['compliance']['score']
    
    # Renewable energy
    if env_metrics.get('renewable_energy'):
        progress['renewable_energy'] = env_metrics['renewable_energy']['percentage']
    
    # Waste reduction (simplified calculation)
    if env_metrics.get('waste_management'):
        waste_kg = env_metrics['waste_management']['total_waste_kg']
        # Assume target is 50% reduction from 10000kg baseline
        baseline = 10000
        reduction_pct = ((baseline - waste_kg) / baseline) * 100
        progress['waste_reduction'] = max(0, min(100, reduction_pct))
    
    return progress


def _format_time_ago(dt):
    """Format datetime as 'time ago' string"""
    if not dt:
        return "Unknown"
    
    # Ensure dt is timezone-aware
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "Just now"