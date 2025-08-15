from django.db import models
from django.conf import settings
import uuid


class Company(models.Model):
    """
    Company model matching the onboard.html business information form
    """
    SECTOR_CHOICES = [
        ('hospitality', 'Hospitality & Tourism'),
        ('construction', 'Construction & Real Estate'),
        ('logistics', 'Logistics & Transportation'),
        ('retail', 'Retail & E-commerce'),
        ('manufacturing', 'Manufacturing'),
        ('technology', 'Technology & Software'),
        ('finance', 'Finance & Banking'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]
    
    EMPLOYEE_SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    ]
    
    EMIRATE_CHOICES = [
        ('abu-dhabi', 'Abu Dhabi'),
        ('dubai', 'Dubai'),
        ('sharjah', 'Sharjah'),
        ('ajman', 'Ajman'),
        ('umm-al-quwain', 'Umm Al Quwain'),
        ('ras-al-khaimah', 'Ras Al Khaimah'),
        ('fujairah', 'Fujairah'),
    ]
    
    LICENSE_TYPE_CHOICES = [
        ('commercial', 'Commercial'),
        ('professional', 'Professional'),
        ('industrial', 'Industrial'),
        ('tourism', 'Tourism'),
        ('free-zone', 'Free Zone'),
    ]
    
    # Basic Information (from onboard.html step 1)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Business Name')
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Company Description',
        help_text='Brief description of the company and its activities'
    )
    business_sector = models.CharField(
        max_length=50, 
        choices=SECTOR_CHOICES,
        verbose_name='Industry'
    )
    employee_size = models.CharField(
        max_length=20,
        choices=EMPLOYEE_SIZE_CHOICES,
        verbose_name='Number of Employees',
        null=True,
        blank=True
    )
    
    # Location Information
    main_location = models.CharField(
        max_length=255, 
        default='Dubai, UAE',
        verbose_name='Main Location'
    )
    emirate = models.CharField(
        max_length=50,
        choices=EMIRATE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Emirates Location'
    )
    license_type = models.CharField(
        max_length=50,
        choices=LICENSE_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Business License Type'
    )
    
    # ESG Setup Status
    esg_scoping_completed = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
    setup_step = models.IntegerField(default=1)  # Tracks current setup step (1-4)
    
    # ESG Data
    scoping_data = models.JSONField(
        default=dict, 
        blank=True,
        help_text='ESG scoping questionnaire responses'
    )
    
    # Company Metrics (calculated from ESG data)
    overall_esg_score = models.FloatField(default=0.0)
    environmental_score = models.FloatField(default=0.0)
    social_score = models.FloatField(default=0.0)
    governance_score = models.FloatField(default=0.0)
    
    # Progress Tracking (matching tracker.html)
    data_completion_percentage = models.FloatField(default=0.0)
    evidence_completion_percentage = models.FloatField(default=0.0)
    total_fields = models.IntegerField(default=0)
    completed_fields = models.IntegerField(default=0)
    total_evidence_files = models.IntegerField(default=0)
    uploaded_evidence_files = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def admin_users(self):
        """Get company admin users"""
        return self.users.filter(role='admin')
    
    @property
    def total_users(self):
        """Get total number of users"""
        return self.users.count()
    
    def update_esg_scores(self):
        """Update ESG scores based on completed tasks and data"""
        # This would be implemented based on your ESG calculation logic
        # For now, return placeholder values
        pass
    
    def update_progress_metrics(self):
        """Update progress tracking metrics"""
        # Calculate data completion
        if self.total_fields > 0:
            self.data_completion_percentage = (self.completed_fields / self.total_fields) * 100
        
        # Calculate evidence completion  
        if self.total_evidence_files > 0:
            self.evidence_completion_percentage = (self.uploaded_evidence_files / self.total_evidence_files) * 100
        
        self.save()


class Location(models.Model):
    """
    Company locations/facilities (from onboard.html step 2)
    Supports multiple locations per company
    """
    BUILDING_TYPE_CHOICES = [
        ('office', 'Office Building'),
        ('retail', 'Retail Space'),
        ('warehouse', 'Warehouse'),
        ('manufacturing', 'Manufacturing Facility'),
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurant'),
        ('mixed', 'Mixed Use'),
        ('other', 'Other'),
    ]
    
    OWNERSHIP_TYPE_CHOICES = [
        ('owned', 'Owned'),
        ('leased', 'Leased'),
        ('managed', 'Managed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='locations'
    )
    
    # Basic Information
    name = models.CharField(max_length=255, verbose_name='Location Name')
    address = models.TextField(verbose_name='Full Address')
    emirate = models.CharField(
        max_length=50,
        choices=Company.EMIRATE_CHOICES,
        verbose_name='Emirate'
    )
    
    # Building Details
    total_floor_area = models.FloatField(
        help_text='Total floor area in square meters',
        null=True,
        blank=True
    )
    number_of_floors = models.IntegerField(null=True, blank=True)
    building_type = models.CharField(
        max_length=50,
        choices=BUILDING_TYPE_CHOICES,
        null=True,
        blank=True
    )
    ownership_type = models.CharField(
        max_length=20,
        choices=OWNERSHIP_TYPE_CHOICES,
        null=True,
        blank=True
    )
    
    # Operational Details
    operating_hours = models.CharField(
        max_length=100,
        blank=True,
        help_text='e.g., 8:00 AM - 6:00 PM'
    )
    number_of_employees = models.IntegerField(null=True, blank=True)
    
    # Utility Information
    has_separate_meters = models.BooleanField(default=False)
    meters_info = models.JSONField(
        default=list,
        blank=True,
        help_text='Information about utility meters (electricity, water, gas)'
    )
    
    # ESG Relevance
    is_primary = models.BooleanField(
        default=False,
        help_text='Primary location for ESG reporting'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class CompanySettings(models.Model):
    """
    Company-specific settings and preferences
    """
    REPORT_FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annual', 'Semi-Annual'),
        ('annual', 'Annual'),
    ]
    
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='settings'
    )
    
    # Reporting Preferences
    default_report_frequency = models.CharField(
        max_length=20,
        choices=REPORT_FREQUENCY_CHOICES,
        default='quarterly'
    )
    
    # Notification Settings
    email_notifications = models.BooleanField(default=True)
    task_reminders = models.BooleanField(default=True)
    report_reminders = models.BooleanField(default=True)
    
    # Framework Preferences
    active_frameworks = models.JSONField(
        default=list,
        help_text='List of active ESG frameworks'
    )
    
    # Target Settings
    targets = models.JSONField(
        default=dict,
        help_text='Company ESG targets and goals'
    )
    
    # Custom Fields
    custom_fields = models.JSONField(
        default=dict,
        help_text='Company-specific custom fields'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'
    
    def __str__(self):
        return f"{self.company.name} Settings"


class CompanyInvitation(models.Model):
    """
    Handle user invitations to join companies
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_sent_invitations'
    )
    
    # Invitation Details
    email = models.EmailField()
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'ESG Manager'),
        ('contributor', 'Contributor'),
        ('viewer', 'Viewer'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='contributor'
    )
    message = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Security
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    
    # Response
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='company_accepted_invitations'
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Company Invitation'
        verbose_name_plural = 'Company Invitations'
        ordering = ['-created_at']
        unique_together = ['company', 'email']
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.company.name}"