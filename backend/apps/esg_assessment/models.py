from django.db import models
from django.conf import settings
import uuid


class ESGFramework(models.Model):
    """
    ESG frameworks supported by the platform
    (DST, Green Key, GRI, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=255)
    description = models.TextField()
    version = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Framework metadata
    organization = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ESG Framework'
        verbose_name_plural = 'ESG Frameworks'
        ordering = ['display_name']
    
    def __str__(self):
        return self.display_name


class ESGCategory(models.Model):
    """
    ESG categories (Environmental, Social, Governance)
    """
    CATEGORY_CHOICES = [
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fa-solid fa-chart-line')
    color = models.CharField(max_length=20, default='#2EC57D')
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'ESG Category'
        verbose_name_plural = 'ESG Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.display_name


class ESGSubcategory(models.Model):
    """
    ESG subcategories for more granular organization
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        ESGCategory,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'ESG Subcategory'
        verbose_name_plural = 'ESG Subcategories'
        ordering = ['category', 'order', 'name']
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.category.display_name} - {self.display_name}"


class ESGQuestion(models.Model):
    """
    ESG assessment questions for different sectors
    """
    QUESTION_TYPES = [
        ('yes_no', 'Yes/No'),
        ('multiple_choice', 'Multiple Choice'),
        ('text', 'Text Input'),
        ('number', 'Number Input'),
        ('date', 'Date Input'),
        ('file_upload', 'File Upload'),
        ('rating', 'Rating Scale'),
    ]
    
    PRIORITY_LEVELS = [
        ('required', 'Required'),
        ('recommended', 'Recommended'),
        ('optional', 'Optional'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Question organization
    category = models.ForeignKey(
        ESGCategory,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    subcategory = models.ForeignKey(
        ESGSubcategory,
        on_delete=models.CASCADE,
        related_name='questions',
        null=True,
        blank=True
    )
    
    # Question content
    question_text = models.TextField(verbose_name='Question')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    help_text = models.TextField(blank=True)
    placeholder = models.CharField(max_length=255, blank=True)
    
    # Question properties
    is_required = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default='recommended'
    )
    order = models.IntegerField(default=0)
    
    # Applicable sectors
    applicable_sectors = models.JSONField(
        default=list,
        help_text='List of business sectors this question applies to'
    )
    
    # Framework mapping
    frameworks = models.ManyToManyField(
        ESGFramework,
        related_name='questions',
        blank=True
    )
    
    # Validation rules
    validation_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text='Validation rules for the question (min, max, pattern, etc.)'
    )
    
    # Multiple choice options (if applicable)
    options = models.JSONField(
        default=list,
        blank=True,
        help_text='Options for multiple choice questions'
    )
    
    # Scoring and weighting
    weight = models.FloatField(
        default=1.0,
        help_text='Weight of this question in category scoring'
    )
    scoring_criteria = models.JSONField(
        default=dict,
        blank=True,
        help_text='Scoring criteria for different answers'
    )
    
    # Compliance context
    compliance_context = models.TextField(
        blank=True,
        help_text='Why this question is important for compliance'
    )
    
    # Question metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ESG Question'
        verbose_name_plural = 'ESG Questions'
        ordering = ['category', 'subcategory', 'order']
    
    def __str__(self):
        return f"{self.category.name} - {self.question_text[:50]}..."
    
    @property
    def short_question(self):
        """Return truncated question text"""
        if len(self.question_text) > 100:
            return self.question_text[:97] + "..."
        return self.question_text


class ESGAssessment(models.Model):
    """
    ESG assessment instance for a company
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    
    # Assessment details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assessment_period_start = models.DateField()
    assessment_period_end = models.DateField()
    
    # Status and progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    progress_percentage = models.FloatField(default=0.0)
    
    # Scores
    overall_score = models.FloatField(default=0.0)
    environmental_score = models.FloatField(default=0.0)
    social_score = models.FloatField(default=0.0)
    governance_score = models.FloatField(default=0.0)
    
    # Framework compliance
    target_frameworks = models.ManyToManyField(
        ESGFramework,
        related_name='assessments',
        blank=True
    )
    
    # Assessment metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_assessments'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_assessments'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'ESG Assessment'
        verbose_name_plural = 'ESG Assessments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"
    
    def calculate_scores(self):
        """Calculate ESG scores based on responses"""
        # This would implement the actual scoring logic
        # For now, return placeholder calculations
        responses = self.responses.all()
        if not responses:
            return
        
        # Calculate category scores
        categories = ['environmental', 'social', 'governance']
        category_scores = {}
        
        for category in categories:
            category_responses = responses.filter(
                question__category__name=category
            )
            if category_responses:
                # Implement scoring logic here
                category_scores[category] = 75.0  # Placeholder
        
        # Update scores
        self.environmental_score = category_scores.get('environmental', 0)
        self.social_score = category_scores.get('social', 0)
        self.governance_score = category_scores.get('governance', 0)
        self.overall_score = sum(category_scores.values()) / len(category_scores) if category_scores else 0
        
        self.save()


class ESGResponse(models.Model):
    """
    User responses to ESG questions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(
        ESGAssessment,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        ESGQuestion,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # Response data (flexible to handle different question types)
    response_data = models.JSONField(
        help_text='The actual response data'
    )
    
    # Response metadata
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    confidence_level = models.IntegerField(
        default=5,
        help_text='Confidence level from 1-10'
    )
    notes = models.TextField(blank=True)
    
    # Evidence and supporting documents
    has_evidence = models.BooleanField(default=False)
    evidence_description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ESG Response'
        verbose_name_plural = 'ESG Responses'
        unique_together = ['assessment', 'question']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.assessment} - {self.question.short_question}"


class ESGEvidence(models.Model):
    """
    Evidence files supporting ESG responses
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    response = models.ForeignKey(
        ESGResponse,
        on_delete=models.CASCADE,
        related_name='evidence_files'
    )
    
    # File information
    file = models.FileField(upload_to='esg_evidence/')
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    
    # Evidence metadata
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    
    # Upload metadata
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'ESG Evidence'
        verbose_name_plural = 'ESG Evidence'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.response} - {self.original_filename}"


class SectorQuestionMapping(models.Model):
    """
    Maps questions to specific business sectors
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sector = models.CharField(
        max_length=50,
        choices=settings.ESG_SECTORS.items() if hasattr(settings, 'ESG_SECTORS') else []
    )
    question = models.ForeignKey(
        ESGQuestion,
        on_delete=models.CASCADE,
        related_name='sector_mappings'
    )
    is_required = models.BooleanField(default=False)
    priority = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = 'Sector Question Mapping'
        verbose_name_plural = 'Sector Question Mappings'
        unique_together = ['sector', 'question']
        ordering = ['sector', 'priority']
    
    def __str__(self):
        return f"{self.sector} - {self.question.short_question}"