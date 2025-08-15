from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import (
    ESGFramework, ESGCategory, ESGQuestion, ESGAssessment,
    ESGResponse, ESGEvidence, SectorQuestionMapping
)
from .serializers import (
    ESGFrameworkSerializer, ESGCategorySerializer, ESGQuestionSerializer,
    ESGAssessmentSerializer, ESGResponseSerializer, SectorQuestionsSerializer,
    ESGScopingSerializer, ComplianceCheckSerializer
)
from apps.tasks.models import Task

logger = logging.getLogger(__name__)


class ESGFrameworkViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ESG frameworks"""
    queryset = ESGFramework.objects.filter(is_active=True)
    serializer_class = ESGFrameworkSerializer
    permission_classes = [IsAuthenticated]


class ESGCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ESG categories"""
    queryset = ESGCategory.objects.all()
    serializer_class = ESGCategorySerializer
    permission_classes = [IsAuthenticated]


class ESGQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ESG questions"""
    queryset = ESGQuestion.objects.filter(is_active=True)
    serializer_class = ESGQuestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter questions based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by sector if provided
        sector = self.request.query_params.get('sector')
        if sector:
            queryset = queryset.filter(applicable_sectors__contains=[sector])
        
        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        
        # Filter by framework if provided
        framework = self.request.query_params.get('framework')
        if framework:
            queryset = queryset.filter(frameworks__name=framework)
        
        return queryset.order_by('category__order', 'order')


class ESGAssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for ESG assessments"""
    serializer_class = ESGAssessmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return assessments for user's company"""
        if self.request.user.company:
            return ESGAssessment.objects.filter(
                company=self.request.user.company
            ).order_by('-created_at')
        return ESGAssessment.objects.none()
    
    def perform_create(self, serializer):
        """Set company and creator when creating assessment"""
        serializer.save(
            company=self.request.user.company,
            created_by=self.request.user
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sectors(request):
    """
    Get available business sectors
    Matches frontend expectation from onboard.html
    """
    sectors = []
    
    if hasattr(settings, 'ESG_SECTORS'):
        for key, name in settings.ESG_SECTORS.items():
            sectors.append({
                'id': key,
                'name': name,
                'description': f'{name} sector ESG assessment'
            })
    
    return Response({
        'sectors': sectors,
        'total_sectors': len(sectors)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sector_questions(request, sector):
    """
    Get questions for a specific sector
    Matches frontend expectation from onboard.html step 3
    """
    # Validate sector
    if hasattr(settings, 'ESG_SECTORS'):
        if sector not in settings.ESG_SECTORS:
            return Response({
                'error': f'Invalid sector: {sector}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get questions for this sector
    questions = ESGQuestion.objects.filter(
        is_active=True,
        applicable_sectors__contains=[sector]
    ).select_related('category', 'subcategory').prefetch_related('frameworks')
    
    # Organize questions by category
    questions_by_category = {}
    categories = set()
    frameworks = set()
    
    for question in questions:
        category_name = question.category.display_name
        categories.add(category_name)
        
        if category_name not in questions_by_category:
            questions_by_category[category_name] = []
        
        # Add framework names
        for framework in question.frameworks.all():
            frameworks.add(framework.display_name)
        
        # Format question data matching frontend expectations
        question_data = {
            'id': str(question.id),
            'question': question.question_text,
            'type': question.question_type,
            'required': question.is_required,
            'category': question.category.name,
            'frameworks': [f.display_name for f in question.frameworks.all()],
            'help_text': question.help_text,
            'options': question.options if question.question_type == 'multiple_choice' else None,
            'validation_rules': question.validation_rules,
            'compliance_context': question.compliance_context
        }
        
        questions_by_category[category_name].append(question_data)
    
    response_data = {
        'sector': sector,
        'sector_name': settings.ESG_SECTORS.get(sector, sector) if hasattr(settings, 'ESG_SECTORS') else sector,
        'total_questions': questions.count(),
        'categories': list(categories),
        'questions_by_category': questions_by_category,
        'frameworks': list(frameworks)
    }
    
    serializer = SectorQuestionsSerializer(response_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_esg_scoping(request):
    """
    Complete ESG scoping process (onboard.html step 3)
    Creates assessment and generates tasks
    """
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ESGScopingSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    scoping_data = serializer.validated_data
    company = request.user.company
    
    try:
        # Create ESG assessment
        assessment_name = f"{company.name} ESG Assessment {timezone.now().year}"
        
        assessment = ESGAssessment.objects.create(
            company=company,
            name=assessment_name,
            description="Initial ESG assessment from onboarding",
            assessment_period_start=scoping_data.get(
                'assessment_period_start',
                timezone.now().date()
            ),
            assessment_period_end=scoping_data.get(
                'assessment_period_end',
                (timezone.now() + timedelta(days=365)).date()
            ),
            status='in_progress',
            created_by=request.user
        )
        
        # Add target frameworks
        if scoping_data.get('selected_frameworks'):
            frameworks = ESGFramework.objects.filter(
                name__in=scoping_data['selected_frameworks']
            )
            assessment.target_frameworks.set(frameworks)
        
        # Save responses
        responses_created = 0
        for question_id, response_data in scoping_data['responses'].items():
            try:
                question = ESGQuestion.objects.get(id=question_id)
                
                ESGResponse.objects.create(
                    assessment=assessment,
                    question=question,
                    response_data=response_data,
                    answered_by=request.user,
                    confidence_level=response_data.get('confidence', 5)
                )
                responses_created += 1
                
            except ESGQuestion.DoesNotExist:
                logger.warning(f"Question {question_id} not found")
                continue
        
        # Generate tasks based on responses
        tasks_created = self._generate_tasks_from_scoping(
            company, assessment, scoping_data
        )
        
        # Update company scoping status
        company.scoping_data = scoping_data
        company.esg_scoping_completed = True
        company.setup_step = max(company.setup_step, 4)
        company.save()
        
        # Calculate initial scores
        assessment.calculate_scores()
        
        logger.info(
            f"ESG scoping completed for {company.name}: "
            f"{responses_created} responses, {len(tasks_created)} tasks created"
        )
        
        return Response({
            'message': 'ESG scoping completed successfully',
            'assessment_id': str(assessment.id),
            'responses_created': responses_created,
            'tasks_generated': len(tasks_created),
            'sector': scoping_data['sector'],
            'company_id': str(company.id),
            'next_step': 'evidence_upload'
        })
        
    except Exception as e:
        logger.error(f"Error completing ESG scoping: {e}")
        return Response({
            'error': 'Failed to complete ESG scoping. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _generate_tasks_from_scoping(company, assessment, scoping_data):
    """Generate tasks based on ESG scoping responses"""
    tasks_created = []
    
    # Get unanswered questions for this sector
    sector = scoping_data['sector']
    unanswered_questions = ESGQuestion.objects.filter(
        applicable_sectors__contains=[sector],
        is_active=True
    ).exclude(
        id__in=scoping_data['responses'].keys()
    )
    
    # Create tasks for unanswered required questions
    for question in unanswered_questions.filter(is_required=True):
        task = Task.objects.create(
            company=company,
            title=f"Complete: {question.question_text[:50]}...",
            description=question.question_text,
            category=question.category.name,
            status='todo',
            priority='high' if question.priority == 'required' else 'medium',
            frameworks=[f.name for f in question.frameworks.all()],
            compliance_context=question.compliance_context,
            action_required=f"Provide answer for: {question.question_text}"
        )
        tasks_created.append(task)
    
    # Create evidence upload tasks for questions that need documentation
    evidence_questions = ESGQuestion.objects.filter(
        id__in=scoping_data['responses'].keys(),
        question_type='file_upload'
    )
    
    for question in evidence_questions:
        task = Task.objects.create(
            company=company,
            title=f"Upload Evidence: {question.question_text[:40]}...",
            description=f"Upload supporting documents for: {question.question_text}",
            category=question.category.name,
            status='todo',
            priority='medium',
            frameworks=[f.name for f in question.frameworks.all()],
            compliance_context=question.compliance_context,
            action_required="Upload supporting documentation"
        )
        tasks_created.append(task)
    
    return tasks_created


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_frameworks(request):
    """Get available ESG frameworks"""
    frameworks = ESGFramework.objects.filter(is_active=True)
    
    framework_data = []
    for framework in frameworks:
        framework_data.append({
            'id': str(framework.id),
            'name': framework.name,
            'display_name': framework.display_name,
            'description': framework.description,
            'organization': framework.organization
        })
    
    return Response({
        'frameworks': framework_data,
        'total_frameworks': len(framework_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_compliance(request, framework_name):
    """Check compliance status for a specific framework"""
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        framework = ESGFramework.objects.get(name=framework_name)
    except ESGFramework.DoesNotExist:
        return Response({
            'error': f'Framework {framework_name} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get latest assessment for the company
    latest_assessment = ESGAssessment.objects.filter(
        company=request.user.company
    ).order_by('-created_at').first()
    
    if not latest_assessment:
        return Response({
            'error': 'No assessment found for company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get required questions for this framework
    required_questions = ESGQuestion.objects.filter(
        frameworks=framework,
        is_active=True,
        is_required=True
    )
    
    # Check how many are answered
    answered_questions = ESGResponse.objects.filter(
        assessment=latest_assessment,
        question__in=required_questions
    )
    
    compliance_percentage = (
        answered_questions.count() / required_questions.count() * 100
        if required_questions.count() > 0 else 0
    )
    
    # Get missing questions
    answered_question_ids = answered_questions.values_list('question_id', flat=True)
    missing_questions = required_questions.exclude(id__in=answered_question_ids)
    
    compliance_data = {
        'framework': framework.display_name,
        'compliance_percentage': compliance_percentage,
        'required_questions': required_questions.count(),
        'answered_questions': answered_questions.count(),
        'missing_questions': [
            {
                'id': str(q.id),
                'question': q.question_text,
                'category': q.category.name
            }
            for q in missing_questions
        ],
        'recommendations': [
            'Complete all required questions',
            'Upload supporting evidence',
            'Review and verify responses'
        ] if compliance_percentage < 100 else ['Framework compliance complete']
    }
    
    serializer = ComplianceCheckSerializer(compliance_data)
    return Response(serializer.data)