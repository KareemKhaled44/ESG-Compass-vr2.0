from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import (
    TeamInvitation, UserProfile, TeamRole, UserActivity,
    TeamCollaboration, CollaborationParticipant, UserSession, CompanySettings
)

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    company_name = serializers.CharField(source='user.company.name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'user_email', 'user_name', 'company_name',
            'job_title', 'department', 'phone_number', 'timezone',
            'bio', 'expertise_areas', 'certifications',
            'avatar', 'linkedin_url',
            'email_notifications', 'task_notifications',
            'report_notifications', 'weekly_digest',
            'last_activity', 'total_tasks_completed',
            'total_reports_generated', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user_email', 'user_name', 'company_name',
            'last_activity', 'total_tasks_completed',
            'total_reports_generated', 'created_at', 'updated_at'
        ]


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for team members list"""
    profile = UserProfileSerializer(read_only=True)
    is_online = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role', 'department', 'is_active', 'status',
            'date_joined', 'last_login', 'profile', 'is_online'
        ]
        read_only_fields = ['date_joined', 'last_login']
    
    def get_is_online(self, obj):
        """Check if user is currently online"""
        if not obj.last_login:
            return False
        # Consider user online if last login was within 15 minutes
        return (timezone.now() - obj.last_login) < timedelta(minutes=15)
    
    def get_status(self, obj):
        """Convert is_active boolean to readable status"""
        return 'active' if obj.is_active else 'inactive'


class TeamInvitationSerializer(serializers.ModelSerializer):
    """Serializer for team invitations"""
    invited_by_name = serializers.CharField(source='invited_by.full_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TeamInvitation
        fields = [
            'id', 'email', 'role', 'message', 'status',
            'invited_by_name', 'company_name', 'is_expired',
            'created_at', 'expires_at', 'responded_at'
        ]
        read_only_fields = [
            'id', 'status', 'invited_by_name', 'company_name',
            'is_expired', 'created_at', 'expires_at', 'responded_at'
        ]


class CreateInvitationSerializer(serializers.ModelSerializer):
    """Serializer for creating team invitations"""
    
    class Meta:
        model = TeamInvitation
        fields = ['email', 'role', 'message']
    
    def validate_email(self, value):
        """Validate that email is not already a team member"""
        company = self.context['request'].user.company
        
        # Check if user already exists in the company
        if User.objects.filter(email=value, company=company).exists():
            raise serializers.ValidationError(
                "This email is already associated with a team member."
            )
        
        # Check for pending invitations
        if TeamInvitation.objects.filter(
            email=value,
            company=company,
            status='pending'
        ).exists():
            raise serializers.ValidationError(
                "A pending invitation already exists for this email."
            )
        
        return value
    
    def create(self, validated_data):
        """Create invitation with auto-generated expiry"""
        company = self.context['request'].user.company
        invited_by = self.context['request'].user
        
        invitation = TeamInvitation.objects.create(
            company=company,
            invited_by=invited_by,
            expires_at=timezone.now() + timedelta(days=7),
            **validated_data
        )
        
        return invitation


class TeamRoleSerializer(serializers.ModelSerializer):
    """Serializer for team roles"""
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamRole
        fields = [
            'id', 'name', 'description', 'permissions',
            'is_default', 'is_active', 'created_by_name',
            'users_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name', 'created_at', 'updated_at']
    
    def get_users_count(self, obj):
        """Count users with this role"""
        # This would need to be implemented based on how roles are assigned
        return 0


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activities"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user_name', 'activity_type', 'description',
            'metadata', 'ip_address', 'created_at'
        ]
        read_only_fields = ['created_at']


class TeamCollaborationSerializer(serializers.ModelSerializer):
    """Serializer for team collaborations"""
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    participants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamCollaboration
        fields = [
            'id', 'collaboration_type', 'title', 'description',
            'owner_name', 'participants_count', 'is_active',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['owner_name', 'created_at', 'updated_at']
    
    def get_participants_count(self, obj):
        """Count collaboration participants"""
        return obj.participants.count()


class CollaborationParticipantSerializer(serializers.ModelSerializer):
    """Serializer for collaboration participants"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = CollaborationParticipant
        fields = [
            'user_name', 'user_email', 'permission_level',
            'joined_at', 'last_accessed', 'contributions_count',
            'comments_count'
        ]
        read_only_fields = [
            'user_name', 'user_email', 'joined_at',
            'last_accessed', 'contributions_count', 'comments_count'
        ]


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    duration_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user_name', 'ip_address', 'device_type',
            'browser', 'location', 'started_at', 'last_activity',
            'ended_at', 'is_active', 'duration_formatted'
        ]
        read_only_fields = [
            'user_name', 'started_at', 'last_activity',
            'ended_at', 'duration_formatted'
        ]
    
    def get_duration_formatted(self, obj):
        """Format session duration"""
        if obj.ended_at and obj.started_at:
            duration = obj.ended_at - obj.started_at
            hours = duration.total_seconds() // 3600
            minutes = (duration.total_seconds() % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m"
        elif obj.is_active:
            duration = timezone.now() - obj.started_at
            hours = duration.total_seconds() // 3600
            minutes = (duration.total_seconds() % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m (active)"
        return "Unknown"


class CompanySettingsSerializer(serializers.ModelSerializer):
    """Serializer for company user management settings"""
    
    class Meta:
        model = CompanySettings
        fields = [
            'allow_self_registration', 'require_email_verification',
            'default_user_role', 'password_expiry_days',
            'require_2fa', 'session_timeout_hours',
            'allow_external_sharing', 'max_team_size',
            'admin_notification_email', 'notify_on_new_user',
            'notify_on_role_change', 'updated_at'
        ]
        read_only_fields = ['updated_at']


class TeamStatisticsSerializer(serializers.Serializer):
    """Serializer for team statistics"""
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    pending_invitations = serializers.IntegerField()
    roles_distribution = serializers.DictField()
    department_distribution = serializers.DictField()
    recent_activity_count = serializers.IntegerField()
    average_session_duration = serializers.FloatField()
    
    # Activity metrics
    tasks_completed_this_month = serializers.IntegerField()
    reports_generated_this_month = serializers.IntegerField()
    assessments_completed_this_month = serializers.IntegerField()
    
    # Collaboration metrics
    active_collaborations = serializers.IntegerField()
    total_collaborations = serializers.IntegerField()


class UserPermissionsSerializer(serializers.Serializer):
    """Serializer for user permissions check"""
    can_invite_users = serializers.BooleanField()
    can_manage_roles = serializers.BooleanField()
    can_view_reports = serializers.BooleanField()
    can_manage_assessments = serializers.BooleanField()
    can_export_data = serializers.BooleanField()
    can_manage_settings = serializers.BooleanField()
    can_delete_users = serializers.BooleanField()
    can_assign_tasks = serializers.BooleanField()


class InviteAcceptSerializer(serializers.Serializer):
    """Serializer for accepting invitations"""
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(max_length=255)
    
    def validate_token(self, value):
        """Validate invitation token"""
        try:
            invitation = TeamInvitation.objects.get(
                token=value,
                status='pending'
            )
            
            if invitation.is_expired:
                raise serializers.ValidationError("Invitation has expired.")
            
            self.invitation = invitation
            return value
            
        except TeamInvitation.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired invitation token.")
    
    def create(self, validated_data):
        """Create user account and accept invitation"""
        invitation = self.invitation
        
        # Create user account
        user = User.objects.create_user(
            email=invitation.email,
            password=validated_data['password'],
            full_name=validated_data['full_name']
        )
        
        # Accept invitation
        invitation.accept(user)
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class BulkInviteSerializer(serializers.Serializer):
    """Serializer for bulk invitations"""
    invitations = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=20
    )
    
    def validate_invitations(self, value):
        """Validate bulk invitation data"""
        validated_invitations = []
        emails = set()
        
        for invitation_data in value:
            if 'email' not in invitation_data:
                raise serializers.ValidationError("Each invitation must include an email.")
            
            email = invitation_data['email']
            
            # Check for duplicate emails in batch
            if email in emails:
                raise serializers.ValidationError(f"Duplicate email found: {email}")
            
            emails.add(email)
            
            # Validate individual invitation
            invitation_serializer = CreateInvitationSerializer(
                data=invitation_data,
                context=self.context
            )
            
            if not invitation_serializer.is_valid():
                raise serializers.ValidationError(
                    f"Invalid data for {email}: {invitation_serializer.errors}"
                )
            
            validated_invitations.append(invitation_serializer.validated_data)
        
        return validated_invitations
    
    def create(self, validated_data):
        """Create bulk invitations"""
        company = self.context['request'].user.company
        invited_by = self.context['request'].user
        invitations = []
        
        for invitation_data in validated_data['invitations']:
            invitation = TeamInvitation.objects.create(
                company=company,
                invited_by=invited_by,
                expires_at=timezone.now() + timedelta(days=7),
                **invitation_data
            )
            invitations.append(invitation)
        
        return invitations


class TeamOverviewSerializer(serializers.Serializer):
    """Serializer for team overview dashboard"""
    team_statistics = TeamStatisticsSerializer()
    recent_members = TeamMemberSerializer(many=True)
    pending_invitations = TeamInvitationSerializer(many=True)
    recent_activities = UserActivitySerializer(many=True)
    active_sessions = UserSessionSerializer(many=True)


class RoleUpdateSerializer(serializers.Serializer):
    """Serializer for updating user roles"""
    user_id = serializers.UUIDField()
    new_role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    
    def validate_user_id(self, value):
        """Validate user exists in company"""
        company = self.context['request'].user.company
        
        try:
            user = User.objects.get(id=value, company=company)
            self.user = user
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found in your company.")
    
    def validate(self, attrs):
        """Additional validation"""
        # Prevent users from changing their own role
        if self.user == self.context['request'].user:
            raise serializers.ValidationError("You cannot change your own role.")
        
        return attrs