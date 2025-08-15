from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reports'

router = DefaultRouter()
router.register('templates', views.ReportTemplateViewSet)
router.register('generated', views.GeneratedReportViewSet, basename='generated_report')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Report dashboard and generation
    path('dashboard/', views.report_dashboard, name='report_dashboard'),
    path('generate/', views.generate_report, name='generate_report'),
    path('generate-custom/', views.generate_custom_report, name='generate_custom_report'),
    
    # Report management
    path('history/', views.report_history, name='report_history'),
    path('delete/<uuid:report_id>/', views.delete_report, name='delete_report'),
    
    # Compliance tracking
    path('compliance-status/', views.compliance_status, name='compliance_status'),
    
    # Shared reports (public access)
    path('shared/<str:access_token>/', views.shared_report_access, name='shared_report_access'),
    path('shared/<str:access_token>/download/', views.shared_report_download, name='shared_report_download'),
]