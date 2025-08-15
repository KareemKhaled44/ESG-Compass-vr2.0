from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta, date
import logging
import uuid

from .models import ReportTemplate, GeneratedReport, ReportSchedule, ReportAccess
from .serializers import (
    ReportTemplateSerializer, GeneratedReportSerializer, ReportGenerationRequestSerializer,
    ReportScheduleSerializer, ReportDashboardSerializer, ComplianceStatusSerializer,
    ReportShareSerializer, CustomReportConfigSerializer
)
from .utils import generate_report_pdf, generate_report_excel

logger = logging.getLogger(__name__)


class ReportTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for report templates"""
    queryset = ReportTemplate.objects.filter(status='active')
    serializer_class = ReportTemplateSerializer
    permission_classes = []  # Allow public access to browse templates
    
    def get_queryset(self):
        """Filter templates based on company sector"""
        queryset = super().get_queryset()
        
        # Check if user is authenticated and has a company
        if hasattr(self.request.user, 'company') and self.request.user.company:
            sector = self.request.user.company.business_sector
            # For SQLite compatibility, we'll filter in Python instead of database
            # In production with PostgreSQL, you can use __contains lookup
            # For now, return all templates since filtering is optional
            pass
        
        return queryset


class GeneratedReportViewSet(viewsets.ModelViewSet):
    """ViewSet for generated reports"""
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return reports for user's company"""
        if self.request.user.company:
            return GeneratedReport.objects.filter(
                company=self.request.user.company
            ).select_related(
                'template', 'generated_by'
            ).order_by('-created_at')
        return GeneratedReport.objects.none()
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download generated report file"""
        report = self.get_object()
        
        # DEBUG: Log download request details
        logger.info(f"🔽 Download request for report ID: {pk}")
        logger.info(f"🔽 Report object: {report.name}")
        logger.info(f"🔽 Report file path: {report.file.path if report.file else 'None'}")
        
        if not report.file:
            logger.error(f"❌ No file found for report {pk}")
            return Response({
                'error': 'Report file not available'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if report.is_expired:
            logger.error(f"❌ Report {pk} has expired")
            return Response({
                'error': 'Report has expired'
            }, status=status.HTTP_410_GONE)
        
        # Log access
        ReportAccess.objects.create(
            report=report,
            accessed_by=request.user,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            access_type='download'
        )
        
        # Get file content and log details
        try:
            file_content = report.file.read()
            logger.info(f"✅ Successfully read file: {len(file_content)} bytes")
            
            # Construct safe filename
            safe_filename = f"{report.name.replace('/', '_').replace(':', '_')}.{report.format}"
            logger.info(f"📁 Download filename: {safe_filename}")
            
            # Return file response
            response = HttpResponse(
                file_content,
                content_type='application/pdf' if report.format == 'pdf' else 'application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error reading file for report {pk}: {e}")
            return Response({
                'error': f'Error reading report file: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share report with external users"""
        report = self.get_object()
        serializer = ReportShareSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        share_data = serializer.validated_data
        
        # Generate access token
        access_token = str(uuid.uuid4())
        
        # Set expiry
        expires_at = timezone.now() + timedelta(days=share_data['expires_in_days'])
        
        # Update report sharing settings
        report.is_shared = True
        report.access_token = access_token
        report.expires_at = expires_at
        report.shared_with = share_data['email_addresses']
        report.save()
        
        # In production, send email notifications here
        
        logger.info(f"Report {report.name} shared with {len(share_data['email_addresses'])} recipients")
        
        return Response({
            'message': 'Report shared successfully',
            'access_token': access_token,
            'expires_at': expires_at,
            'shared_with': share_data['email_addresses']
        })
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_dashboard(request):
    """
    Get report dashboard data for report.html
    """
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    company = request.user.company
    
    # Get available templates
    templates = ReportTemplate.objects.filter(
        status='active'
    ).filter(
        models.Q(applicable_sectors__contains=[company.business_sector]) |
        models.Q(applicable_sectors=[])
    )
    
    # Get recent reports
    recent_reports = GeneratedReport.objects.filter(
        company=company
    ).order_by('-created_at')[:10]
    
    # Calculate statistics
    total_reports = GeneratedReport.objects.filter(company=company).count()
    reports_this_month = GeneratedReport.objects.filter(
        company=company,
        created_at__gte=timezone.now().replace(day=1)
    ).count()
    pending_reports = GeneratedReport.objects.filter(
        company=company,
        status__in=['pending', 'generating']
    ).count()
    
    # Check capabilities
    dst_ready = company.data_completion_percentage > 85
    green_key_ready = company.data_completion_percentage > 70
    
    dashboard_data = {
        'available_templates': ReportTemplateSerializer(templates, many=True).data,
        'recent_reports': GeneratedReportSerializer(recent_reports, many=True).data,
        'total_reports_generated': total_reports,
        'reports_this_month': reports_this_month,
        'pending_reports': pending_reports,
        'can_generate_dst': dst_ready,
        'can_generate_green_key': green_key_ready,
        'data_completeness_overall': company.data_completion_percentage or 75.0
    }
    
    serializer = ReportDashboardSerializer(dashboard_data)
    return Response(serializer.data)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """
    Generate a new report based on template and parameters
    """
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ReportGenerationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        template = ReportTemplate.objects.get(
            id=data['template_id'],
            status='active'
        )
    except ReportTemplate.DoesNotExist:
        return Response({
            'error': 'Report template not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Create report generation record
    report_name = data.get('name') or f"{template.display_name} - {data['period_start']} to {data['period_end']}"
    
    report = GeneratedReport.objects.create(
        company=request.user.company,
        template=template,
        name=report_name,
        description=data.get('description', ''),
        format=data['format'],
        period_start=data['period_start'],
        period_end=data['period_end'],
        parameters=data.get('parameters', {}),
        generated_by=request.user,
        status='generating',
        access_token=str(uuid.uuid4())
    )
    
    try:
        # Generate report based on format
        if data['format'] == 'pdf':
            file_path = generate_report_pdf(report)
        elif data['format'] == 'xlsx':
            file_path = generate_report_excel(report)
        else:
            # For other formats, use basic generation
            file_path = generate_report_pdf(report)  # Fallback to PDF
        
        # Mark as completed
        report.mark_completed(file_path)
        
        logger.info(f"Report generated successfully: {report.name}")
        
        return Response({
            'message': 'Report generated successfully',
            'report': GeneratedReportSerializer(report).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        report.mark_failed(str(e))
        
        return Response({
            'error': 'Report generation failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_custom_report(request):
    """
    Generate custom report with user-defined configuration
    """
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CustomReportConfigSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    config = serializer.validated_data
    
    # Get custom export template
    try:
        template = ReportTemplate.objects.get(
            report_type='custom_export',
            status='active'
        )
    except ReportTemplate.DoesNotExist:
        return Response({
            'error': 'Custom export template not available'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Create custom report
    report = GeneratedReport.objects.create(
        company=request.user.company,
        template=template,
        name=config['name'],
        description=config.get('description', ''),
        format=config['format'],
        period_start=config['period_start'],
        period_end=config['period_end'],
        parameters=config,
        generated_by=request.user,
        status='generating',
        access_token=str(uuid.uuid4())
    )
    
    try:
        # Generate custom report
        if config['format'] == 'pdf':
            file_path = generate_report_pdf(report)
        else:
            file_path = generate_report_excel(report)
        
        report.mark_completed(file_path)
        
        return Response({
            'message': 'Custom report generated successfully',
            'report': GeneratedReportSerializer(report).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Custom report generation failed: {e}")
        report.mark_failed(str(e))
        
        return Response({
            'error': 'Custom report generation failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compliance_status(request):
    """
    Get compliance status for various frameworks
    Matches compliance tracker in report.html
    """
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    company = request.user.company
    
    # Mock compliance data matching report.html
    compliance_data = [
        {
            'framework': 'Dubai Sustainable Tourism',
            'compliance_percentage': 87.0,
            'status': 'compliant',
            'missing_requirements': [
                'Water consumption tracking',
                'Waste diversion metrics'
            ],
            'last_updated': timezone.now() - timedelta(days=1),
            'next_review_date': date.today() + timedelta(days=90)
        },
        {
            'framework': 'Green Key Certification',
            'compliance_percentage': 73.0,
            'status': 'partial',
            'missing_requirements': [
                'Environmental policy documentation',
                'Staff training records',
                'Energy efficiency measures'
            ],
            'last_updated': timezone.now() - timedelta(days=5),
            'next_review_date': date.today() + timedelta(days=60)
        },
        {
            'framework': 'UAE Federal Climate Law',
            'compliance_percentage': 68.0,
            'status': 'non_compliant',
            'missing_requirements': [
                'Carbon footprint assessment',
                'Emission reduction plan',
                'Renewable energy adoption'
            ],
            'last_updated': timezone.now() - timedelta(days=2),
            'next_review_date': date.today() + timedelta(days=30)
        }
    ]
    
    serializer = ComplianceStatusSerializer(compliance_data, many=True)
    return Response({
        'compliance_status': serializer.data,
        'overall_compliance': 76.0,
        'total_frameworks': len(compliance_data),
        'compliant_frameworks': len([f for f in compliance_data if f['status'] == 'compliant'])
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_history(request):
    """Get report generation history"""
    if not request.user.company:
        return Response({
            'error': 'User is not associated with any company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    reports = GeneratedReport.objects.filter(
        company=request.user.company
    ).order_by('-created_at')
    
    # Apply filters
    status_filter = request.query_params.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    template_filter = request.query_params.get('template')
    if template_filter:
        reports = reports.filter(template__report_type=template_filter)
    
    # Pagination
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    paginator.page_size = 20
    page = paginator.paginate_queryset(reports, request)
    
    serializer = GeneratedReportSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_report(request, report_id):
    """Delete a generated report"""
    try:
        report = GeneratedReport.objects.get(
            id=report_id,
            company=request.user.company
        )
    except GeneratedReport.DoesNotExist:
        return Response({
            'error': 'Report not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Delete file if exists
    if report.file:
        report.file.delete()
    
    report.delete()
    
    return Response({
        'message': 'Report deleted successfully'
    })


# Public endpoint for shared reports (no authentication required)
@api_view(['GET'])
def shared_report_access(request, access_token):
    """Access shared report via token"""
    try:
        report = GeneratedReport.objects.get(
            access_token=access_token,
            is_shared=True
        )
    except GeneratedReport.DoesNotExist:
        raise Http404("Shared report not found")
    
    if report.is_expired:
        return Response({
            'error': 'Shared report has expired'
        }, status=status.HTTP_410_GONE)
    
    # Log access
    ReportAccess.objects.create(
        report=report,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        access_type='view'
    )
    
    # Return report metadata (not the file itself)
    return Response({
        'report': {
            'name': report.name,
            'description': report.description,
            'format': report.format,
            'period_start': report.period_start,
            'period_end': report.period_end,
            'generated_at': report.created_at,
            'company_name': report.company.name,
            'expires_at': report.expires_at
        },
        'download_url': f'/api/reports/shared/{access_token}/download/'
    })


@api_view(['GET'])
def shared_report_download(request, access_token):
    """Download shared report file"""
    try:
        report = GeneratedReport.objects.get(
            access_token=access_token,
            is_shared=True
        )
    except GeneratedReport.DoesNotExist:
        raise Http404("Shared report not found")
    
    if report.is_expired:
        return Response({
            'error': 'Shared report has expired'
        }, status=status.HTTP_410_GONE)
    
    if not report.file:
        return Response({
            'error': 'Report file not available'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Log download
    ReportAccess.objects.create(
        report=report,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        access_type='download'
    )
    
    # Return file
    response = HttpResponse(
        report.file.read(),
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{report.name}.{report.format}"'
    
    return response