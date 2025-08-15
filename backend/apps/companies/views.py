from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging

from .models import Company, Location, CompanySettings, CompanyInvitation
from .serializers import (
    CompanySerializer, LocationSerializer, CompanyUpdateSerializer,
    BusinessInfoSerializer, LocationDataSerializer, CompanySettingsSerializer,
    CompanyInvitationSerializer, DashboardStatsSerializer, ProgressTrackerSerializer
)

logger = logging.getLogger(__name__)


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for company management
    Handles company CRUD operations and related actions
    """
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    def _calculate_category_progress(self, company, category):
        """Calculate progress percentage for a specific ESG category based on task progress bars"""
        from apps.tasks.models import Task
        from django.db.models import Avg
        
        category_tasks = Task.objects.filter(company=company, category=category)
        
        if not category_tasks.exists():
            return 0.0
            
        # Average the progress_percentage of all tasks in this category
        avg_progress = category_tasks.aggregate(avg_progress=Avg('progress_percentage'))['avg_progress']
        
        return round(avg_progress or 0.0, 1)
    
    def _get_category_task_details(self, company):
        """Get detailed task status for each ESG category"""
        from apps.tasks.models import Task
        
        details = {}
        
        for category in ['environmental', 'social', 'governance']:
            tasks = Task.objects.filter(company=company, category=category)
            category_details = {}
            
            for task in tasks:
                # Create a simplified key from task title
                key = task.title.lower().replace(' ', '_').replace('&', 'and')[:20]
                
                # Use actual task status
                if task.status == 'completed':
                    status = 'complete'
                elif task.status in ['in_progress', 'started']:
                    status = 'in_progress'
                else:
                    status = 'pending'
                    
                category_details[key] = status
            
            details[category] = category_details
            
        return details
    
    def get_queryset(self):
        """Only return companies the user belongs to"""
        if self.request.user.company:
            return Company.objects.filter(id=self.request.user.company.id)
        return Company.objects.none()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's company information
        Used by frontend to get company data
        """
        if not request.user.company:
            return Response({
                'error': 'User is not associated with any company'
            }, status=status.HTTP_404_NOT_FOUND)
        
        company = request.user.company
        serializer = self.get_serializer(company)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_business_info(self, request):
        """
        Update business information (onboard.html step 1)
        """
        if not request.user.company:
            return Response({
                'error': 'User is not associated with any company'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BusinessInfoSerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.update_company(request.user.company)
            
            logger.info(f"Business info updated for company: {company.name}")
            
            return Response({
                'message': 'Business information updated successfully',
                'company': CompanySerializer(company).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_locations(self, request):
        """
        Update company locations (onboard.html step 2)
        """
        if not request.user.company:
            return Response({
                'error': 'User is not associated with any company'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LocationDataSerializer(data=request.data)
        if serializer.is_valid():
            locations = serializer.create_locations(request.user.company)
            
            logger.info(f"Locations updated for company: {request.user.company.name}")
            
            return Response({
                'message': 'Locations updated successfully',
                'locations_count': len(locations),
                'locations': LocationSerializer(locations, many=True).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_scoping_data(self, request):
        """
        Update ESG scoping data (onboarding questionnaire answers)
        """
        if not request.user.company:
            return Response({
                'error': 'User is not associated with any company'
            }, status=status.HTTP_404_NOT_FOUND)
        
        company = request.user.company
        scoping_data = request.data.get('scoping_data', {})
        
        # Merge with existing scoping data
        if company.scoping_data:
            company.scoping_data.update(scoping_data)
        else:
            company.scoping_data = scoping_data
        
        # Update completion status if provided
        if request.data.get('esg_scoping_completed') is not None:
            company.esg_scoping_completed = request.data.get('esg_scoping_completed')
        
        if request.data.get('setup_step') is not None:
            company.setup_step = request.data.get('setup_step')
            
        if request.data.get('onboarding_completed') is not None:
            company.onboarding_completed = request.data.get('onboarding_completed')
            logger.info(f"🎯 Onboarding completion status set to: {company.onboarding_completed}")
            
            # Generate initial tasks when onboarding is completed
            if company.onboarding_completed:
                logger.info(f"🚀 Starting task generation for company: {company.name}")
                logger.info(f"   Company locations: {company.locations.count()}")
                
                # Create Location objects from scoping data if they don't exist
                if company.locations.count() == 0:
                    logger.info("📍 No locations found, creating from scoping data...")
                    self._create_locations_from_scoping_data(company, scoping_data)
                    logger.info(f"   Created {company.locations.count()} locations")
                
                from apps.tasks.utils import generate_initial_tasks_for_company
                generated_tasks = generate_initial_tasks_for_company(company, created_by=request.user)
                logger.info(f"✅ Generated {len(generated_tasks)} initial tasks for {company.name}")
        
        company.save()
        
        logger.info(f"ESG scoping data updated for company: {company.name}")
        
        return Response({
            'message': 'ESG scoping data updated successfully',
            'company': CompanySerializer(company).data
        })
    
    def _create_locations_from_scoping_data(self, company, scoping_data):
        """Create Location objects from frontend location data stored in scoping_data"""
        from .models import Location
        
        # Get location data from different possible keys
        location_data = None
        if 'final_location_data' in scoping_data:
            location_data = scoping_data['final_location_data']
        elif 'step_2_locations' in scoping_data:
            location_data = scoping_data['step_2_locations']
        elif 'locations' in scoping_data:
            location_data = scoping_data['locations']
            
        if not location_data:
            logger.warning("No location data found in scoping_data")
            return
            
        logger.info(f"Processing location data: {len(location_data) if isinstance(location_data, list) else 'single location'}")
        
        # Handle both single location and list of locations
        if not isinstance(location_data, list):
            location_data = [location_data] if location_data else []
        
        for idx, loc_data in enumerate(location_data):
            if not loc_data:
                continue
                
            # Create location with meter data
            location = Location.objects.create(
                company=company,
                name=loc_data.get('name', f'Location {idx + 1}'),
                address=loc_data.get('address', ''),
                emirate=loc_data.get('emirate', 'dubai'),
                total_floor_area=float(loc_data.get('totalFloorArea', 0) or 0),
                number_of_floors=int(loc_data.get('numberOfFloors', 1) or 1),
                building_type=loc_data.get('buildingType', ''),
                ownership_type=loc_data.get('ownershipType', ''),
                has_separate_meters=len(loc_data.get('meters', [])) > 0,
                meters_info=loc_data.get('meters', []),  # This preserves the frontend meter format!
                is_primary=(idx == 0)
            )
            logger.info(f"   Created location: {location.name} with {len(loc_data.get('meters', []))} meters")
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """
        Get dashboard statistics (dash.html)
        """
        if not request.user.company:
            return Response({
                'error': 'User is not associated with any company'
            }, status=status.HTTP_404_NOT_FOUND)
        
        company = request.user.company
        
        # Prepare dashboard data matching frontend expectations
        stats_data = {
            'overall_esg_score': company.overall_esg_score or 75.0,
            'environmental_score': company.environmental_score or 72.0,
            'social_score': company.social_score or 78.0,
            'governance_score': company.governance_score or 75.0,
            'data_completion': company.data_completion_percentage,
            'evidence_completion': company.evidence_completion_percentage,
            'recent_uploads': 3,  # This would be calculated from actual data
            'pending_tasks': company.tasks.filter(status='todo').count(),
            'carbon_neutral_progress': 65.0,
            'employee_satisfaction': 82.0,
            'governance_compliance': 90.0,
            'esg_trends': {
                'environmental': [65, 67, 68, 70, 69, 71, 72, 73, 71, 72, 73, 72],
                'social': [70, 72, 74, 75, 76, 77, 78, 77, 78, 79, 78, 78],
                'governance': [68, 69, 70, 71, 72, 73, 74, 75, 74, 75, 76, 75]
            },
            'emissions_breakdown': {
                'electricity': 45,
                'transportation': 30,
                'waste': 15,
                'other': 10
            }
        }
        
        serializer = DashboardStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def progress_tracker(self, request):
        """
        Get progress tracker data (tracker.html)
        FIXED: Now correctly counts actual uploaded files from TaskAttachment model
        """
        if not request.user.company:
            return Response({
                'error': 'User is not associated with any company'
            }, status=status.HTTP_404_NOT_FOUND)
        
        company = request.user.company
        
        # Get all tasks for the company
        from apps.tasks.models import Task, TaskAttachment
        
        all_tasks = Task.objects.filter(company=company)
        
        # Calculate file-based progress
        total_tasks = all_tasks.count()
        
        # Helper function to determine expected files for a task
        def get_expected_files(task):
            title_lower = task.title.lower()
            action_lower = (task.action_required or '').lower()
            combined = f"{title_lower} {action_lower}"
            
            # Check for meter reading tasks (need 3 monthly bills)
            if 'meter:' in title_lower and 'monthly consumption' in action_lower:
                return 3  # 3 months of ADDC bills
            # Check for monthly tracking tasks
            elif ('track' in combined and 'monthly' in combined) or 'monthly consumption' in action_lower:
                return 3  # 3 months of data
            # Check for utility bills/tracking tasks
            elif 'bill' in combined or 'invoice' in combined or 'utility' in combined:
                return 3  # 3 months of bills
            # Check for emissions monitoring (reports + permits)
            elif 'emissions' in combined or 'air quality' in combined:
                return 2  # Monitoring data + permits
            # Check for waste management (tracking + disposal)
            elif 'waste' in combined and ('disposal' in combined or 'track' in combined):
                return 2  # Waste tracking + disposal records
            # Check for recycling programs
            elif 'recycling' in combined or 'reuse' in combined:
                return 2  # Process diagrams + records
            # Check for wastewater treatment
            elif 'wastewater' in combined:
                return 2  # Treatment reports + compliance
            # Default to 1 file for certificates, assessments, etc.
            else:
                return 1
        
        # Calculate detailed progress
        total_expected_files = 0
        total_uploaded_files = 0
        
        # Category-specific counters
        category_progress = {
            'environmental': {'expected': 0, 'uploaded': 0, 'tasks': []},
            'social': {'expected': 0, 'uploaded': 0, 'tasks': []},
            'governance': {'expected': 0, 'uploaded': 0, 'tasks': []},
        }
        
        # Process each task
        for task in all_tasks:
            expected = get_expected_files(task)
            uploaded = task.attachments.count()  # Count actual attachments
            
            total_expected_files += expected
            total_uploaded_files += uploaded
            
            # Track by category
            category = task.category if task.category in category_progress else 'environmental'
            category_progress[category]['expected'] += expected
            category_progress[category]['uploaded'] += uploaded
            
            # Store task details for frontend
            task_detail = {
                'id': str(task.id),
                'title': task.title[:50] + '...' if len(task.title) > 50 else task.title,
                'expected': expected,
                'uploaded': uploaded,
                'status': 'complete' if uploaded >= expected else 'in_progress' if uploaded > 0 else 'pending'
            }
            category_progress[category]['tasks'].append(task_detail)
        
        # Calculate percentages
        def calc_percentage(uploaded, expected):
            return round((uploaded / expected * 100) if expected > 0 else 0, 1)
        
        # Overall progress
        evidence_completion_pct = calc_percentage(total_uploaded_files, total_expected_files)
        data_completion_pct = evidence_completion_pct  # Use same for both for now
        
        # Category percentages
        env_pct = calc_percentage(
            category_progress['environmental']['uploaded'],
            category_progress['environmental']['expected']
        )
        social_pct = calc_percentage(
            category_progress['social']['uploaded'],
            category_progress['social']['expected']
        )
        gov_pct = calc_percentage(
            category_progress['governance']['uploaded'],
            category_progress['governance']['expected']
        )
        
        # Generate category details for frontend display
        category_details = {}
        
        for category, data in category_progress.items():
            category_details[category] = {}
            for task in data['tasks'][:4]:  # Show first 4 tasks
                # Create simple key from task title
                key = task['title'].lower().replace(' ', '_')[:20]
                category_details[category][key] = task['status']
        
        # Generate next actions based on incomplete tasks
        next_actions = []
        
        # Find tasks that need evidence
        tasks_needing_evidence = all_tasks.filter(
            attachments__isnull=True
        ).distinct()[:3]
        
        for task in tasks_needing_evidence:
            next_actions.append({
                'type': 'upload',
                'title': f'Upload evidence for: {task.title[:30]}...',
                'description': task.action_required or 'Upload required documentation',
                'action': 'Upload'
            })
        
        # If no pending tasks, show completion message
        if not next_actions:
            next_actions.append({
                'type': 'complete',
                'title': 'All evidence uploaded!',
                'description': 'Great job! All required files have been uploaded.',
                'action': 'View Report'
            })
        
        progress_data = {
            'data_entered_percentage': data_completion_pct,
            'evidence_uploaded_percentage': evidence_completion_pct,
            'total_fields': total_expected_files,  # Using files as "fields"
            'completed_fields': total_uploaded_files,
            'total_evidence_files': total_expected_files,
            'uploaded_evidence_files': total_uploaded_files,
            'environmental_progress': env_pct,
            'social_progress': social_pct,
            'governance_progress': gov_pct,
            'category_details': category_details,
            'next_actions': next_actions
        }
        
        # Log the calculation for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Progress Tracker Calculation for {company.name}:")
        logger.info(f"  Total tasks: {total_tasks}")
        logger.info(f"  Total expected files: {total_expected_files}")
        logger.info(f"  Total uploaded files: {total_uploaded_files}")
        logger.info(f"  Evidence percentage: {evidence_completion_pct}%")
        logger.info(f"  Environmental: {env_pct}% ({category_progress['environmental']['uploaded']}/{category_progress['environmental']['expected']})")
        logger.info(f"  Social: {social_pct}% ({category_progress['social']['uploaded']}/{category_progress['social']['expected']})")
        logger.info(f"  Governance: {gov_pct}% ({category_progress['governance']['uploaded']}/{category_progress['governance']['expected']})")
        
        serializer = ProgressTrackerSerializer(progress_data)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def company_locations(request):
    """Get all locations for user's company"""
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    locations = Location.objects.filter(company=request.user.company)
    serializer = LocationSerializer(locations, many=True)
    
    return Response({
        'locations': serializer.data,
        'total_locations': len(serializer.data)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_location(request):
    """Add a new location to user's company"""
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data.copy()
    data['company'] = request.user.company.id
    
    serializer = LocationSerializer(data=data)
    if serializer.is_valid():
        location = serializer.save()
        
        logger.info(f"New location added: {location.name} for company: {request.user.company.name}")
        
        return Response({
            'message': 'Location added successfully',
            'location': LocationSerializer(location).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def company_settings(request):
    """Get or update company settings"""
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get or create settings
    settings_obj, created = CompanySettings.objects.get_or_create(
        company=request.user.company
    )
    
    if request.method == 'GET':
        serializer = CompanySettingsSerializer(settings_obj)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CompanySettingsSerializer(
            settings_obj, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            
            logger.info(f"Settings updated for company: {request.user.company.name}")
            
            return Response({
                'message': 'Settings updated successfully',
                'settings': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def company_overview(request):
    """
    Get company overview data for various frontend components
    Used by multiple pages that need company summary data
    """
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    company = request.user.company
    
    # Calculate some basic statistics
    total_tasks = company.tasks.count()
    completed_tasks = company.tasks.filter(status='completed').count()
    pending_tasks = company.tasks.filter(status='todo').count()
    in_progress_tasks = company.tasks.filter(status='in_progress').count()
    
    overview_data = {
        'company': CompanySerializer(company).data,
        'statistics': {
            'total_users': company.total_users,
            'total_locations': company.locations.count(),
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'task_completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        },
        'recent_activity': [
            {
                'type': 'upload',
                'message': 'Energy consumption data uploaded',
                'time': '2 hours ago',
                'icon': 'upload'
            },
            {
                'type': 'report',
                'message': 'DST report generated successfully',
                'time': '1 day ago',
                'icon': 'file'
            },
            {
                'type': 'user',
                'message': 'New team member added',
                'time': '3 days ago',
                'icon': 'user-plus'
            }
        ]
    }
    
    return Response(overview_data)