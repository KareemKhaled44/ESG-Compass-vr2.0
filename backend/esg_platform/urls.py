"""
URL configuration for esg_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from apps.dashboard.views import test_social_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Test dashboard (no auth required)
    path('test/social/', test_social_dashboard, name='test_social_dashboard'),
    
    # API endpoints
    path('api/auth/', include('apps.authentication.urls')),
    path('api/companies/', include('apps.companies.urls')),
    path('api/esg/', include('apps.esg_assessment.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/users/', include('apps.user_management.urls')),
    
    # Serve frontend files (for development)
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)