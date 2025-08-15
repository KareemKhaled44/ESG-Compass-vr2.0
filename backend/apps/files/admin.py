from django.contrib import admin
from .models import ExtractedFileData


class ExtractedFileDataAdmin(admin.ModelAdmin):
    list_display = [
        'task_attachment', 
        'extraction_method', 
        'confidence_score', 
        'processing_status',
        'extraction_date'
    ]
    list_filter = [
        'processing_status', 
        'extraction_method', 
        'extraction_date'
    ]
    search_fields = [
        'task_attachment__original_filename',
        'task_attachment__task__title'
    ]
    readonly_fields = ['extraction_date', 'extracted_json']


admin.site.register(ExtractedFileData, ExtractedFileDataAdmin)