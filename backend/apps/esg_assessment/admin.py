from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ESGFramework, ESGCategory, ESGSubcategory, ESGQuestion,
    ESGAssessment, ESGResponse, ESGEvidence, SectorQuestionMapping
)


@admin.register(ESGFramework)
class ESGFrameworkAdmin(admin.ModelAdmin):
    """ESG Framework admin interface"""
    list_display = ['display_name', 'name', 'version', 'organization', 'is_active', 'created_at']
    list_filter = ['is_active', 'organization', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['display_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description', 'version')
        }),
        ('Organization', {
            'fields': ('organization', 'website', 'documentation_url')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ESGCategory)
class ESGCategoryAdmin(admin.ModelAdmin):
    """ESG Category admin interface"""
    list_display = ['display_name', 'name', 'icon', 'color', 'order']
    list_editable = ['order']
    ordering = ['order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Display', {
            'fields': ('icon', 'color', 'order')
        })
    )


@admin.register(ESGSubcategory)
class ESGSubcategoryAdmin(admin.ModelAdmin):
    """ESG Subcategory admin interface"""
    list_display = ['display_name', 'category', 'name', 'order']
    list_filter = ['category']
    list_editable = ['order']
    search_fields = ['name', 'display_name', 'category__display_name']
    ordering = ['category', 'order']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(ESGQuestion)
class ESGQuestionAdmin(admin.ModelAdmin):
    """ESG Question admin interface"""
    list_display = [
        'short_question', 'category', 'question_type', 
        'is_required', 'priority', 'weight', 'is_active'
    ]
    list_filter = [
        'category', 'question_type', 'is_required', 
        'priority', 'is_active', 'created_at'
    ]
    search_fields = ['question_text', 'help_text', 'compliance_context']
    filter_horizontal = ['frameworks']
    ordering = ['category', 'order']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Question Content', {
            'fields': ('question_text', 'question_type', 'help_text', 'placeholder')
        }),
        ('Organization', {
            'fields': ('category', 'subcategory', 'order')
        }),
        ('Properties', {
            'fields': ('is_required', 'priority', 'weight', 'is_active')
        }),
        ('Applicability', {
            'fields': ('applicable_sectors', 'frameworks')
        }),
        ('Validation & Options', {
            'fields': ('validation_rules', 'options', 'scoring_criteria'),
            'classes': ('collapse',)
        }),
        ('Compliance', {
            'fields': ('compliance_context',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'subcategory'
        ).prefetch_related('frameworks')
    
    def short_question(self, obj):
        """Display truncated question text"""
        return obj.short_question
    short_question.short_description = 'Question'


@admin.register(ESGAssessment)
class ESGAssessmentAdmin(admin.ModelAdmin):
    """ESG Assessment admin interface"""
    list_display = [
        'name', 'company', 'status', 'progress_percentage',
        'overall_score', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'completed_at']
    search_fields = ['name', 'company__name', 'description']
    filter_horizontal = ['target_frameworks']
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'progress_percentage', 'overall_score', 
        'environmental_score', 'social_score', 'governance_score',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'name', 'description')
        }),
        ('Assessment Period', {
            'fields': ('assessment_period_start', 'assessment_period_end')
        }),
        ('Status', {
            'fields': ('status', 'created_by', 'reviewed_by')
        }),
        ('Frameworks', {
            'fields': ('target_frameworks',)
        }),
        ('Scores', {
            'fields': (
                'progress_percentage', 'overall_score',
                'environmental_score', 'social_score', 'governance_score'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'created_by', 'reviewed_by'
        )


@admin.register(ESGResponse)
class ESGResponseAdmin(admin.ModelAdmin):
    """ESG Response admin interface"""
    list_display = [
        'assessment', 'question_short', 'answered_by',
        'confidence_level', 'has_evidence', 'updated_at'
    ]
    list_filter = [
        'assessment__company', 'question__category',
        'confidence_level', 'has_evidence', 'created_at'
    ]
    search_fields = [
        'assessment__name', 'question__question_text',
        'answered_by__full_name', 'notes'
    ]
    ordering = ['-updated_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Response', {
            'fields': ('assessment', 'question', 'response_data')
        }),
        ('Metadata', {
            'fields': ('answered_by', 'confidence_level', 'notes')
        }),
        ('Evidence', {
            'fields': ('has_evidence', 'evidence_description')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'assessment', 'question', 'answered_by'
        )
    
    def question_short(self, obj):
        """Display truncated question text"""
        return obj.question.short_question
    question_short.short_description = 'Question'


@admin.register(ESGEvidence)
class ESGEvidenceAdmin(admin.ModelAdmin):
    """ESG Evidence admin interface"""
    list_display = [
        'original_filename', 'response_assessment', 'file_size_mb',
        'uploaded_by', 'uploaded_at'
    ]
    list_filter = [
        'mime_type', 'uploaded_at',
        'response__assessment__company'
    ]
    search_fields = [
        'original_filename', 'title', 'description',
        'uploaded_by__full_name'
    ]
    ordering = ['-uploaded_at']
    readonly_fields = ['id', 'file_size', 'mime_type', 'uploaded_at']
    
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'original_filename', 'file_size', 'mime_type')
        }),
        ('Content', {
            'fields': ('title', 'description')
        }),
        ('Association', {
            'fields': ('response', 'uploaded_by')
        }),
        ('Metadata', {
            'fields': ('id', 'uploaded_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'response__assessment', 'uploaded_by'
        )
    
    def response_assessment(self, obj):
        """Display associated assessment"""
        return obj.response.assessment.name
    response_assessment.short_description = 'Assessment'
    
    def file_size_mb(self, obj):
        """Display file size in MB"""
        return f"{obj.file_size / (1024*1024):.2f} MB"
    file_size_mb.short_description = 'Size'


@admin.register(SectorQuestionMapping)
class SectorQuestionMappingAdmin(admin.ModelAdmin):
    """Sector Question Mapping admin interface"""
    list_display = ['sector', 'question_short', 'is_required', 'priority']
    list_filter = ['sector', 'is_required', 'priority']
    list_editable = ['is_required', 'priority']
    search_fields = ['question__question_text']
    ordering = ['sector', 'priority']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question')
    
    def question_short(self, obj):
        """Display truncated question text"""
        return obj.question.short_question
    question_short.short_description = 'Question'