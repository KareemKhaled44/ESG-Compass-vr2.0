from rest_framework import serializers
from .models import Company, Location, CompanySettings, CompanyInvitation


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for company locations"""
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'address', 'emirate', 'total_floor_area',
            'number_of_floors', 'building_type', 'ownership_type',
            'operating_hours', 'number_of_employees', 'has_separate_meters',
            'meters_info', 'is_primary', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CompanySerializer(serializers.ModelSerializer):
    """
    Company serializer matching the frontend expectations
    Includes locations and user count
    """
    locations = LocationSerializer(many=True, read_only=True)
    total_users = serializers.IntegerField(read_only=True)
    admin_users_count = serializers.SerializerMethodField()
    
    # ESG Progress data (for dashboard)
    environmental_percentage = serializers.SerializerMethodField()
    social_percentage = serializers.SerializerMethodField()
    governance_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'business_sector', 'employee_size', 'main_location',
            'emirate', 'license_type', 'esg_scoping_completed', 'onboarding_completed',
            'setup_step', 'scoping_data', 'overall_esg_score', 'environmental_score', 'social_score',
            'governance_score', 'data_completion_percentage', 'evidence_completion_percentage',
            'total_fields', 'completed_fields', 'total_evidence_files', 'uploaded_evidence_files',
            'locations', 'total_users', 'admin_users_count', 'environmental_percentage',
            'social_percentage', 'governance_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_users']
    
    def get_admin_users_count(self, obj):
        """Get count of admin users"""
        return obj.users.filter(role='admin').count()
    
    def get_environmental_percentage(self, obj):
        """Get environmental progress percentage based on actual company data"""
        from apps.tasks.models import Task
        
        # Calculate based on completed environmental tasks
        environmental_tasks = Task.objects.filter(company=obj, category='environmental')
        total_env_tasks = environmental_tasks.count()
        
        if total_env_tasks == 0:
            return obj.environmental_score or 0.0
            
        completed_env_tasks = environmental_tasks.filter(status='completed').count()
        percentage = (completed_env_tasks / total_env_tasks) * 100
        
        # Update company score if significantly different
        if abs(percentage - (obj.environmental_score or 0)) > 5:
            obj.environmental_score = percentage
            obj.save(update_fields=['environmental_score'])
            
        return round(percentage, 1)
    
    def get_social_percentage(self, obj):
        """Get social progress percentage based on actual company data"""
        from apps.tasks.models import Task
        
        social_tasks = Task.objects.filter(company=obj, category='social')
        total_social_tasks = social_tasks.count()
        
        if total_social_tasks == 0:
            return obj.social_score or 0.0
            
        completed_social_tasks = social_tasks.filter(status='completed').count()
        percentage = (completed_social_tasks / total_social_tasks) * 100
        
        if abs(percentage - (obj.social_score or 0)) > 5:
            obj.social_score = percentage
            obj.save(update_fields=['social_score'])
            
        return round(percentage, 1)
    
    def get_governance_percentage(self, obj):
        """Get governance progress percentage based on actual company data"""
        from apps.tasks.models import Task
        
        governance_tasks = Task.objects.filter(company=obj, category='governance')
        total_gov_tasks = governance_tasks.count()
        
        if total_gov_tasks == 0:
            return obj.governance_score or 0.0
            
        completed_gov_tasks = governance_tasks.filter(status='completed').count()
        percentage = (completed_gov_tasks / total_gov_tasks) * 100
        
        if abs(percentage - (obj.governance_score or 0)) > 5:
            obj.governance_score = percentage
            obj.save(update_fields=['governance_score'])
            
        return round(percentage, 1)


class CompanyUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating company information"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'business_sector', 'employee_size', 'main_location',
            'emirate', 'license_type'
        ]
    
    def validate_name(self, value):
        """Ensure company name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Company name cannot be empty.")
        return value


class BusinessInfoSerializer(serializers.Serializer):
    """
    Serializer for onboard.html step 1 - Business Information
    """
    business_name = serializers.CharField(max_length=255)
    industry = serializers.ChoiceField(choices=Company.SECTOR_CHOICES)
    employee_count = serializers.ChoiceField(choices=Company.EMPLOYEE_SIZE_CHOICES)
    emirate_location = serializers.ChoiceField(
        choices=Company.EMIRATE_CHOICES,
        required=False,
        allow_blank=True
    )
    license_type = serializers.ChoiceField(
        choices=Company.LICENSE_TYPE_CHOICES,
        required=False,
        allow_blank=True
    )
    
    def update_company(self, company):
        """Update company with business info"""
        company.name = self.validated_data['business_name']
        company.business_sector = self.validated_data['industry']
        company.employee_size = self.validated_data['employee_count']
        company.emirate = self.validated_data.get('emirate_location')
        company.license_type = self.validated_data.get('license_type')
        company.setup_step = max(company.setup_step, 2)  # Move to step 2
        company.save()
        return company


class LocationDataSerializer(serializers.Serializer):
    """
    Serializer for onboard.html step 2 - Locations
    """
    main_location = serializers.CharField(max_length=255)
    additional_locations = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    
    def create_locations(self, company):
        """Create locations for company"""
        # Clear existing locations
        company.locations.all().delete()
        
        # Create main location
        main_location = Location.objects.create(
            company=company,
            name="Main Location",
            address=self.validated_data['main_location'],
            emirate=company.emirate or 'dubai',
            is_primary=True
        )
        
        # Create additional locations
        additional_locations = []
        for idx, loc_data in enumerate(self.validated_data.get('additional_locations', [])):
            location = Location.objects.create(
                company=company,
                name=loc_data.get('name', f'Location {idx + 2}'),
                address=loc_data.get('address', ''),
                emirate=loc_data.get('emirate', company.emirate or 'dubai'),
                total_floor_area=loc_data.get('floor_area'),
                number_of_floors=loc_data.get('floors'),
                building_type=loc_data.get('building_type'),
                ownership_type=loc_data.get('ownership_type'),
                is_primary=False
            )
            additional_locations.append(location)
        
        # Update company step
        company.setup_step = max(company.setup_step, 3)
        company.save()
        
        return [main_location] + additional_locations


class CompanySettingsSerializer(serializers.ModelSerializer):
    """Serializer for company settings"""
    
    class Meta:
        model = CompanySettings
        fields = [
            'default_report_frequency', 'email_notifications',
            'task_reminders', 'report_reminders', 'active_frameworks',
            'targets', 'custom_fields'
        ]


class CompanyInvitationSerializer(serializers.ModelSerializer):
    """Serializer for company invitations"""
    invited_by_name = serializers.CharField(source='invited_by.full_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = CompanyInvitation
        fields = [
            'id', 'email', 'role', 'message', 'status', 'invited_by_name',
            'company_name', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'expires_at']


class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for dashboard statistics (dash.html)
    """
    overall_esg_score = serializers.FloatField()
    environmental_score = serializers.FloatField()
    social_score = serializers.FloatField()
    governance_score = serializers.FloatField()
    
    # Progress indicators
    data_completion = serializers.FloatField()
    evidence_completion = serializers.FloatField()
    
    # Recent activity
    recent_uploads = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    
    # Targets progress (for dash.html targets section)
    carbon_neutral_progress = serializers.FloatField(default=65.0)
    employee_satisfaction = serializers.FloatField(default=82.0)
    governance_compliance = serializers.FloatField(default=90.0)
    
    # Trends data for charts
    esg_trends = serializers.DictField()
    emissions_breakdown = serializers.DictField()


class ProgressTrackerSerializer(serializers.Serializer):
    """
    Serializer for progress tracker data (tracker.html)
    """
    # Overall progress
    data_entered_percentage = serializers.FloatField()
    evidence_uploaded_percentage = serializers.FloatField()
    total_fields = serializers.IntegerField()
    completed_fields = serializers.IntegerField()
    total_evidence_files = serializers.IntegerField()
    uploaded_evidence_files = serializers.IntegerField()
    
    # Category breakdown
    environmental_progress = serializers.FloatField()
    social_progress = serializers.FloatField()
    governance_progress = serializers.FloatField()
    
    # Detailed breakdown
    category_details = serializers.DictField()
    
    # Next steps
    next_actions = serializers.ListField()