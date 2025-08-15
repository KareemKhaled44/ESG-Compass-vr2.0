from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import EmailValidator
import uuid


class TeamInvitation(models.Model):
    """
    Team invitations for adding new users to companies
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'ESG Manager'),
        ('contributor', 'Contributor'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='team_invitations'
    )
    
    # Invitation details
    email = models.EmailField(validators=[EmailValidator()])
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='contributor')
    message = models.TextField(blank=True, help_text='Optional invitation message')
    
    # Invitation lifecycle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # User management
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_invitations'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Team Invitation'
        verbose_name_plural = 'Team Invitations'
        ordering = ['-created_at']
        unique_together = ['company', 'email', 'status']
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.email} invited to {self.company.name}"
    
    @property
    def is_expired(self):
        """Check if invitation has expired"""
        return timezone.now() > self.expires_at
    
    def accept(self, user):
        """Accept the invitation"""
        if self.status != 'pending':
            raise ValueError("Invitation is not pending")
        
        if self.is_expired:
            self.status = 'expired'
            self.save()
            raise ValueError("Invitation has expired")
        
        self.status = 'accepted'
        self.accepted_by = user
        self.responded_at = timezone.now()
        self.save()
        
        # Update user's company and role
        user.company = self.company
        user.role = self.role
        user.save()
    
    def decline(self):
        """Decline the invitation"""
        if self.status != 'pending':
            raise ValueError("Invitation is not pending")
        
        self.status = 'declined'
        self.responded_at = timezone.now()
        self.save()
    
    def cancel(self):
        """Cancel the invitation"""
        if self.status not in ['pending']:
            raise ValueError("Can only cancel pending invitations")
        
        self.status = 'cancelled'
        self.save()


class UserProfile(models.Model):
    """
    Extended user profile for additional information
    """
    DEPARTMENT_CHOICES = [
        ('sustainability', 'Sustainability'),
        ('operations', 'Operations'),
        ('finance', 'Finance'),
        ('hr', 'Human Resources'),
        ('legal', 'Legal & Compliance'),
        ('it', 'Information Technology'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Additional profile information
    job_title = models.CharField(max_length=255, blank=True)
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        blank=True
    )
    phone_number = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Professional details
    bio = models.TextField(blank=True, help_text='Professional biography')
    expertise_areas = models.JSONField(
        default=list,
        help_text='Areas of ESG expertise'
    )
    certifications = models.JSONField(
        default=list,
        help_text='Professional certifications'
    )
    
    # Profile settings
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    task_notifications = models.BooleanField(default=True)
    report_notifications = models.BooleanField(default=True)
    weekly_digest = models.BooleanField(default=True)
    
    # Activity tracking
    last_activity = models.DateTimeField(null=True, blank=True)
    total_tasks_completed = models.IntegerField(default=0)
    total_reports_generated = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.full_name} Profile"
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


class TeamRole(models.Model):
    """
    Custom team roles with specific permissions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='custom_roles'
    )
    
    # Role details
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Permissions
    permissions = models.JSONField(
        default=dict,
        help_text='Role-specific permissions configuration'
    )
    
    # Role properties
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Team Role'
        verbose_name_plural = 'Team Roles'
        unique_together = ['company', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class UserActivity(models.Model):
    """
    Track user activities for audit and analytics
    """
    ACTIVITY_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('task_created', 'Task Created'),
        ('task_updated', 'Task Updated'),
        ('task_completed', 'Task Completed'),
        ('assessment_started', 'Assessment Started'),
        ('assessment_completed', 'Assessment Completed'),
        ('report_generated', 'Report Generated'),
        ('data_exported', 'Data Exported'),
        ('settings_updated', 'Settings Updated'),
        ('team_invited', 'Team Member Invited'),
        ('role_changed', 'Role Changed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='user_activities'
    )
    
    # Activity details
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type', 'created_at']),
            models.Index(fields=['company', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.activity_type}"


class TeamCollaboration(models.Model):
    """
    Team collaboration features and shared workspaces
    """
    COLLABORATION_TYPES = [
        ('shared_assessment', 'Shared Assessment'),
        ('shared_task', 'Shared Task'),
        ('shared_report', 'Shared Report'),
        ('team_project', 'Team Project'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='collaborations'
    )
    
    # Collaboration details
    collaboration_type = models.CharField(max_length=50, choices=COLLABORATION_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Participants
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_collaborations'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CollaborationParticipant',
        related_name='collaborations'
    )
    
    # Related objects
    related_task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    related_assessment = models.ForeignKey(
        'esg_assessment.ESGAssessment',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    related_report = models.ForeignKey(
        'reports.GeneratedReport',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    settings = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Team Collaboration'
        verbose_name_plural = 'Team Collaborations'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"


class CollaborationParticipant(models.Model):
    """
    Through model for collaboration participants
    """
    PERMISSION_LEVELS = [
        ('view', 'View Only'),
        ('comment', 'View & Comment'),
        ('edit', 'View, Comment & Edit'),
        ('admin', 'Full Access'),
    ]
    
    collaboration = models.ForeignKey(
        TeamCollaboration,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    # Participation details
    permission_level = models.CharField(
        max_length=20,
        choices=PERMISSION_LEVELS,
        default='view'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Contribution tracking
    contributions_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Collaboration Participant'
        verbose_name_plural = 'Collaboration Participants'
        unique_together = ['collaboration', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} in {self.collaboration.title}"


class UserSession(models.Model):
    """
    Track user sessions for security and analytics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    # Session details
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    
    # Session lifecycle
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Session properties
    is_active = models.BooleanField(default=True)
    duration_seconds = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.started_at}"
    
    def end_session(self):
        """End the user session"""
        if self.is_active:
            self.ended_at = timezone.now()
            self.is_active = False
            self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())
            self.save()


class CompanySettings(models.Model):
    """
    Company-specific settings for user management
    """
    company = models.OneToOneField(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='user_management_settings'
    )
    
    # User registration settings
    allow_self_registration = models.BooleanField(default=False)
    require_email_verification = models.BooleanField(default=True)
    default_user_role = models.CharField(max_length=20, default='contributor')
    
    # Security settings
    password_expiry_days = models.IntegerField(default=0)  # 0 = no expiry
    require_2fa = models.BooleanField(default=False)
    session_timeout_hours = models.IntegerField(default=24)
    
    # Collaboration settings
    allow_external_sharing = models.BooleanField(default=False)
    max_team_size = models.IntegerField(default=50)
    
    # Notification settings
    admin_notification_email = models.EmailField(blank=True)
    notify_on_new_user = models.BooleanField(default=True)
    notify_on_role_change = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Company User Settings'
        verbose_name_plural = 'Company User Settings'
    
    def __str__(self):
        return f"{self.company.name} User Settings"