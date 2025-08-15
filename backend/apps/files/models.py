"""
Django models for Universal File Parser
Stores extracted data from uploaded files
"""

import json
import logging
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.cache import cache
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ExtractedFileData(models.Model):
    """
    Model to store extracted data from uploaded files
    Links to TaskAttachment and stores parsed JSON data
    """
    task_attachment = models.OneToOneField(
        'tasks.TaskAttachment',
        on_delete=models.CASCADE,
        related_name='extracted_data'
    )
    
    # Extraction metadata
    extraction_date = models.DateTimeField(auto_now_add=True)
    extraction_method = models.CharField(max_length=50)
    confidence_score = models.FloatField(default=0.0)
    
    # Extracted data as JSON
    extracted_json = models.JSONField(default=dict)
    
    # Quick access fields for common metrics
    energy_consumption_kwh = models.FloatField(null=True, blank=True)
    water_usage_liters = models.FloatField(null=True, blank=True)
    waste_generated_kg = models.FloatField(null=True, blank=True)
    carbon_emissions_tco2 = models.FloatField(null=True, blank=True)
    renewable_energy_percentage = models.FloatField(null=True, blank=True)
    
    total_employees = models.IntegerField(null=True, blank=True)
    training_hours = models.FloatField(null=True, blank=True)
    safety_incidents = models.IntegerField(null=True, blank=True)
    employee_satisfaction_score = models.FloatField(null=True, blank=True)
    
    compliance_score = models.FloatField(null=True, blank=True)
    board_meetings = models.IntegerField(null=True, blank=True)
    
    # Processing status
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Extracted File Data'
        verbose_name_plural = 'Extracted File Data'
        indexes = [
            models.Index(fields=['task_attachment', 'processing_status']),
        ]
    
    def __str__(self):
        return f"Data from {self.task_attachment.original_filename}"


@receiver(post_save, sender='tasks.TaskAttachment')
def extract_data_from_attachment(sender, instance, created, **kwargs):
    """
    Signal handler to automatically extract data when a file is uploaded
    """
    if created:
        # Import here to avoid circular imports
        from .file_parser import UniversalFileParser
        
        # Create extraction record
        extracted_record = ExtractedFileData.objects.create(
            task_attachment=instance,
            processing_status='processing'
        )
        
        try:
            # Try to use the full parser first, fallback to simple parser
            try:
                from .file_parser import UniversalFileParser
                parser = UniversalFileParser()
            except ImportError as e:
                logger.warning(f"Full parser not available, using simple parser: {e}")
                from .simple_parser import SimpleFileParser
                parser = SimpleFileParser()
            
            # Parse the file
            extracted_data = parser.parse_file(
                file_path=instance.original_filename,
                file_obj=instance.file
            )
            
            # Save extracted data
            extracted_record.extraction_method = extracted_data.extraction_method
            extracted_record.confidence_score = extracted_data.confidence_score
            extracted_record.extracted_json = json.loads(extracted_data.to_json())
            
            # Save quick access fields
            extracted_record.energy_consumption_kwh = extracted_data.energy_consumption_kwh
            extracted_record.water_usage_liters = extracted_data.water_usage_liters
            extracted_record.waste_generated_kg = extracted_data.waste_generated_kg
            extracted_record.carbon_emissions_tco2 = extracted_data.carbon_emissions_tco2
            extracted_record.renewable_energy_percentage = extracted_data.renewable_energy_percentage
            
            extracted_record.total_employees = extracted_data.total_employees
            extracted_record.training_hours = extracted_data.training_hours
            extracted_record.safety_incidents = extracted_data.safety_incidents
            extracted_record.employee_satisfaction_score = extracted_data.employee_satisfaction_score
            
            extracted_record.compliance_score = extracted_data.compliance_score
            extracted_record.board_meetings = extracted_data.board_meetings
            
            extracted_record.processing_status = 'completed'
            extracted_record.save()
            
            # Update company metrics cache
            update_company_metrics_cache(instance.task.company)
            
            logger.info(f"Successfully extracted data from {instance.original_filename} with confidence {extracted_data.confidence_score:.1f}%")
            
        except Exception as e:
            logger.error(f"Failed to extract data from {instance.original_filename}: {e}")
            extracted_record.processing_status = 'failed'
            extracted_record.error_message = str(e)
            extracted_record.save()


def update_company_metrics_cache(company):
    """
    Update cached company metrics based on all extracted data
    """
    cache_key = f"company_metrics_{company.id}"
    
    # Aggregate all extracted data for the company
    from django.db.models import Avg, Sum, Max, Min
    from apps.tasks.models import TaskAttachment
    
    attachments = TaskAttachment.objects.filter(
        task__company=company
    ).select_related('extracted_data')
    
    # Calculate aggregated metrics
    metrics = {
        'total_files_processed': 0,
        'average_confidence': 0.0,
        'environmental': {},
        'social': {},
        'governance': {},
        'last_updated': datetime.now().isoformat()
    }
    
    # Get all extracted data
    extracted_data = ExtractedFileData.objects.filter(
        task_attachment__task__company=company,
        processing_status='completed'
    )
    
    if extracted_data.exists():
        metrics['total_files_processed'] = extracted_data.count()
        metrics['average_confidence'] = extracted_data.aggregate(
            avg_confidence=Avg('confidence_score')
        )['avg_confidence'] or 0.0
        
        # Environmental metrics (latest non-null values)
        latest_energy = extracted_data.exclude(
            energy_consumption_kwh__isnull=True
        ).order_by('-extraction_date').first()
        if latest_energy:
            metrics['environmental']['energy_consumption_kwh'] = latest_energy.energy_consumption_kwh
        
        latest_water = extracted_data.exclude(
            water_usage_liters__isnull=True
        ).order_by('-extraction_date').first()
        if latest_water:
            metrics['environmental']['water_usage_liters'] = latest_water.water_usage_liters
        
        latest_waste = extracted_data.exclude(
            waste_generated_kg__isnull=True
        ).order_by('-extraction_date').first()
        if latest_waste:
            metrics['environmental']['waste_generated_kg'] = latest_waste.waste_generated_kg
        
        latest_carbon = extracted_data.exclude(
            carbon_emissions_tco2__isnull=True
        ).order_by('-extraction_date').first()
        if latest_carbon:
            metrics['environmental']['carbon_emissions_tco2'] = latest_carbon.carbon_emissions_tco2
        
        # Social metrics
        latest_employees = extracted_data.exclude(
            total_employees__isnull=True
        ).order_by('-extraction_date').first()
        if latest_employees:
            metrics['social']['total_employees'] = latest_employees.total_employees
        
        avg_training = extracted_data.exclude(
            training_hours__isnull=True
        ).aggregate(avg_training=Avg('training_hours'))
        if avg_training['avg_training']:
            metrics['social']['training_hours_avg'] = avg_training['avg_training']
        
        # Governance metrics
        latest_compliance = extracted_data.exclude(
            compliance_score__isnull=True
        ).order_by('-extraction_date').first()
        if latest_compliance:
            metrics['governance']['compliance_score'] = latest_compliance.compliance_score
    
    # Cache for 1 hour
    cache.set(cache_key, metrics, 3600)
    
    return metrics