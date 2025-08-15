from rest_framework import serializers
from .models import (
    ESGFramework, ESGCategory, ESGSubcategory,
    ESGQuestion, ESGAssessment, ESGResponse, ESGEvidence
)


class ESGFrameworkSerializer(serializers.ModelSerializer):
    """Serializer for ESG frameworks"""
    
    class Meta:
        model = ESGFramework
        fields = [
            'id', 'name', 'display_name', 'description', 'version',
            'organization', 'website', 'is_active'
        ]


class ESGCategorySerializer(serializers.ModelSerializer):
    """Serializer for ESG categories"""
    
    class Meta:
        model = ESGCategory
        fields = [
            'id', 'name', 'display_name', 'description',
            'icon', 'color', 'order'
        ]


class ESGSubcategorySerializer(serializers.ModelSerializer):
    """Serializer for ESG subcategories"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ESGSubcategory
        fields = [
            'id', 'name', 'display_name', 'description',
            'order', 'category_name'
        ]


class ESGQuestionSerializer(serializers.ModelSerializer):
    """Serializer for ESG questions"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    frameworks = ESGFrameworkSerializer(many=True, read_only=True)
    
    class Meta:
        model = ESGQuestion
        fields = [
            'id', 'question_text', 'question_type', 'help_text', 'placeholder',
            'is_required', 'priority', 'order', 'applicable_sectors',
            'validation_rules', 'options', 'weight', 'scoring_criteria',
            'compliance_context', 'category_name', 'subcategory_name',
            'frameworks'
        ]


class ESGEvidenceSerializer(serializers.ModelSerializer):
    """Serializer for ESG evidence files"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = ESGEvidence
        fields = [
            'id', 'file', 'original_filename', 'file_size', 'mime_type',
            'title', 'description', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['file_size', 'mime_type', 'uploaded_at']


class ESGResponseSerializer(serializers.ModelSerializer):
    """Serializer for ESG responses"""
    question = ESGQuestionSerializer(read_only=True)
    question_id = serializers.UUIDField(write_only=True)
    answered_by_name = serializers.CharField(source='answered_by.full_name', read_only=True)
    evidence_files = ESGEvidenceSerializer(many=True, read_only=True)
    
    class Meta:
        model = ESGResponse
        fields = [
            'id', 'question', 'question_id', 'response_data',
            'confidence_level', 'notes', 'has_evidence',
            'evidence_description', 'answered_by_name', 'evidence_files',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ESGAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for ESG assessments"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.full_name', read_only=True)
    target_frameworks = ESGFrameworkSerializer(many=True, read_only=True)
    total_questions = serializers.SerializerMethodField()
    answered_questions = serializers.SerializerMethodField()
    
    class Meta:
        model = ESGAssessment
        fields = [
            'id', 'name', 'description', 'assessment_period_start',
            'assessment_period_end', 'status', 'progress_percentage',
            'overall_score', 'environmental_score', 'social_score',
            'governance_score', 'company_name', 'created_by_name',
            'reviewed_by_name', 'target_frameworks', 'total_questions',
            'answered_questions', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'progress_percentage', 'overall_score', 'environmental_score',
            'social_score', 'governance_score', 'created_at', 'updated_at'
        ]
    
    def get_total_questions(self, obj):
        """Get total number of questions for this assessment"""
        # This would filter based on company sector and target frameworks
        return ESGQuestion.objects.filter(is_active=True).count()
    
    def get_answered_questions(self, obj):
        """Get number of answered questions"""
        return obj.responses.count()


class SectorQuestionsSerializer(serializers.Serializer):
    """
    Serializer for sector-specific questions
    Matches the frontend expectation from onboard.html step 3
    """
    sector = serializers.CharField()
    total_questions = serializers.IntegerField()
    categories = serializers.ListField(child=serializers.CharField())
    questions_by_category = serializers.DictField()
    frameworks = serializers.ListField(child=serializers.CharField())


class ESGScopingSerializer(serializers.Serializer):
    """
    Serializer for ESG scoping data from onboard.html
    """
    sector = serializers.CharField()
    selected_frameworks = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    responses = serializers.DictField()
    assessment_period_start = serializers.DateField(required=False)
    assessment_period_end = serializers.DateField(required=False)
    
    def validate_sector(self, value):
        """Validate that sector exists"""
        from django.conf import settings
        if hasattr(settings, 'ESG_SECTORS'):
            if value not in settings.ESG_SECTORS:
                raise serializers.ValidationError(f"Invalid sector: {value}")
        return value
    
    def validate_responses(self, value):
        """Validate response format"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Responses must be a dictionary")
        return value


class ComplianceCheckSerializer(serializers.Serializer):
    """
    Serializer for compliance checking results
    """
    framework = serializers.CharField()
    compliance_percentage = serializers.FloatField()
    required_questions = serializers.IntegerField()
    answered_questions = serializers.IntegerField()
    missing_questions = serializers.ListField()
    recommendations = serializers.ListField()