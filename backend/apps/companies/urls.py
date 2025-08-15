from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'companies'

router = DefaultRouter()
router.register('', views.CompanyViewSet, basename='company')

urlpatterns = [
    # Company viewset routes (includes /me, /update_business_info, etc.)
    path('', include(router.urls)),
    
    # Additional location endpoints
    path('locations/', views.company_locations, name='company_locations'),
    path('locations/add/', views.add_location, name='add_location'),
    
    # Settings
    path('settings/', views.company_settings, name='company_settings'),
    
    # Overview and statistics
    path('overview/', views.company_overview, name='company_overview'),
]