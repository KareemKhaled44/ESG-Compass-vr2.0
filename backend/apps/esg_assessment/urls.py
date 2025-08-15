from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'esg_assessment'

router = DefaultRouter()
router.register('frameworks', views.ESGFrameworkViewSet)
router.register('categories', views.ESGCategoryViewSet)
router.register('questions', views.ESGQuestionViewSet)
router.register('assessments', views.ESGAssessmentViewSet, basename='assessment')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Sector and question endpoints (matching frontend expectations)
    path('sectors/', views.get_sectors, name='get_sectors'),
    path('sectors/<str:sector>/questions/', views.get_sector_questions, name='get_sector_questions'),
    
    # ESG scoping (onboard.html step 3)
    path('scoping/complete/', views.complete_esg_scoping, name='complete_esg_scoping'),
    
    # Framework operations
    path('frameworks-list/', views.get_frameworks, name='get_frameworks'),
    path('compliance/<str:framework_name>/', views.check_compliance, name='check_compliance'),
]