"""
Management command to process all existing file attachments
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tasks.models import TaskAttachment
from apps.files.models import ExtractedFileData
import json
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process all existing file attachments for ESG data extraction'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reprocess files that have already been processed',
        )
        parser.add_argument(
            '--company-id',
            type=int,
            help='Process files only for a specific company ID',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting file processing...')
        
        # Get all attachments that haven't been processed yet
        queryset = TaskAttachment.objects.all()
        
        if options['company_id']:
            queryset = queryset.filter(task__company_id=options['company_id'])
        
        if not options['force']:
            # Only process files that haven't been processed yet
            processed_ids = ExtractedFileData.objects.values_list('task_attachment_id', flat=True)
            queryset = queryset.exclude(id__in=processed_ids)
        
        total_files = queryset.count()
        self.stdout.write(f'Found {total_files} files to process')
        
        processed = 0
        errors = 0
        
        for attachment in queryset:
            try:
                self.stdout.write(f'Processing: {attachment.original_filename}')
                
                # Check if already exists (for force mode)
                if options['force']:
                    ExtractedFileData.objects.filter(task_attachment=attachment).delete()
                
                # Create extraction record
                extracted_record = ExtractedFileData.objects.create(
                    task_attachment=attachment,
                    processing_status='processing'
                )
                
                try:
                    # Try to use the full parser first, fallback to simple parser
                    try:
                        from apps.files.file_parser import UniversalFileParser
                        parser = UniversalFileParser()
                        parser_type = "Universal"
                    except ImportError as e:
                        self.stdout.write(f'  Using simple parser: {e}')
                        from apps.files.simple_parser import SimpleFileParser
                        parser = SimpleFileParser()
                        parser_type = "Simple"
                    
                    # Parse the file
                    extracted_data = parser.parse_file(
                        file_path=attachment.original_filename,
                        file_obj=attachment.file
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
                    from apps.files.models import update_company_metrics_cache
                    update_company_metrics_cache(attachment.task.company)
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Processed with {parser_type} parser: '
                            f'{extracted_data.confidence_score:.1f}% confidence'
                        )
                    )
                    processed += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Error processing file: {e}')
                    )
                    extracted_record.processing_status = 'failed'
                    extracted_record.error_message = str(e)
                    extracted_record.save()
                    errors += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error creating extraction record: {e}')
                )
                errors += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nProcessing completed!\n'
                f'Processed: {processed}\n'
                f'Errors: {errors}\n'
                f'Total: {total_files}'
            )
        )
        
        # Show summary of extracted data
        if processed > 0:
            self.stdout.write('\n=== Extraction Summary ===')
            all_extracted = ExtractedFileData.objects.filter(processing_status='completed')
            
            from django.db import models
            avg_confidence = all_extracted.aggregate(
                avg=models.Avg('confidence_score')
            )['avg'] or 0
            
            metrics_with_data = {
                'Energy (kWh)': all_extracted.exclude(energy_consumption_kwh__isnull=True).count(),
                'Water (L)': all_extracted.exclude(water_usage_liters__isnull=True).count(),
                'Waste (kg)': all_extracted.exclude(waste_generated_kg__isnull=True).count(),
                'Carbon (tCO2)': all_extracted.exclude(carbon_emissions_tco2__isnull=True).count(),
                'Employees': all_extracted.exclude(total_employees__isnull=True).count(),
                'Training Hours': all_extracted.exclude(training_hours__isnull=True).count(),
                'Compliance Score': all_extracted.exclude(compliance_score__isnull=True).count(),
            }
            
            self.stdout.write(f'Average confidence: {avg_confidence:.1f}%')
            self.stdout.write('Metrics found:')
            for metric, count in metrics_with_data.items():
                self.stdout.write(f'  {metric}: {count} files')