from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    TeamInvitation, UserProfile, TeamRole, UserActivity,
    TeamCollaboration, CollaborationParticipant, UserSession, CompanySettings
)

User = get_user_model()


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    """Team invitation admin interface"""
    list_display = [
        'email', 'company', 'role', 'status',
        'invited_by_display', 'is_expired', 'created_at'
    ]
    list_filter = [
        'status', 'role', 'created_at', 'expires_at'
    ]
    search_fields = ['email', 'company__name', 'invited_by__full_name']
    ordering = ['-created_at']
    readonly_fields = ['id', 'token', 'is_expired', 'created_at', 'responded_at']
    
    fieldsets = (
        ('Invitation Details', {
            'fields': ('company', 'email', 'role', 'message')
        }),
        ('Status', {
            'fields': ('status', 'invited_by', 'accepted_by')
        }),
        ('Timeline', {
            'fields': ('expires_at', 'responded_at')
        }),
        ('Metadata', {
            'fields': ('id', 'token', 'is_expired', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['resend_invitations', 'cancel_invitations']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'invited_by', 'accepted_by'
        )
    
    def invited_by_display(self, obj):
        """Display who sent the invitation"""
        if obj.invited_by:
            return obj.invited_by.full_name
        return '-'
    invited_by_display.short_description = 'Invited By'
    
    def resend_invitations(self, request, queryset):
        """Resend selected invitations"""
        pending_invitations = queryset.filter(status='pending')
        
        for invitation in pending_invitations:
            if invitation.is_expired:
                invitation.expires_at = timezone.now() + timezone.timedelta(days=7)
                invitation.save()
            # TODO: Send invitation email
        
        self.message_user(
            request,
            f"Resent {pending_invitations.count()} invitations."
        )
    resend_invitations.short_description = "Resend selected invitations"
    
    def cancel_invitations(self, request, queryset):
        """Cancel selected pending invitations"""
        cancelled = queryset.filter(status='pending').update(status='cancelled')
        self.message_user(request, f"Cancelled {cancelled} invitations.")
    cancel_invitations.short_description = "Cancel selected invitations"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile admin interface"""
    list_display = [
        'user_display', 'job_title', 'department',
        'company_display', 'last_activity', 'total_tasks_completed'
    ]
    list_filter = [
        'department', 'email_notifications', 'created_at'
    ]
    search_fields = [
        'user__full_name', 'user__email', 'job_title',
        'user__company__name'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'last_activity', 'total_tasks_completed',
        'total_reports_generated', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'job_title', 'department', 'phone_number', 'timezone')
        }),
        ('Professional Details', {
            'fields': ('bio', 'expertise_areas', 'certifications', 'linkedin_url')
        }),
        ('Profile Media', {
            'fields': ('avatar',)
        }),
        ('Notifications', {
            'fields': (
                'email_notifications', 'task_notifications',
                'report_notifications', 'weekly_digest'
            )
        }),
        ('Activity Statistics', {
            'fields': (
                'last_activity', 'total_tasks_completed',
                'total_reports_generated'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'user__company')
    
    def user_display(self, obj):
        """Display user name with link"""
        if obj.user:
            url = reverse('admin:authentication_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.full_name)
        return '-'
    user_display.short_description = 'User'
    
    def company_display(self, obj):
        """Display user's company"""
        if obj.user and obj.user.company:
            return obj.user.company.name
        return '-'
    company_display.short_description = 'Company'


@admin.register(TeamRole)
class TeamRoleAdmin(admin.ModelAdmin):
    """Team role admin interface"""
    list_display = [
        'name', 'company', 'is_default', 'is_active',
        'created_by_display', 'created_at'
    ]
    list_filter = ['is_default', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'company__name']
    ordering = ['company', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Role Information', {
            'fields': ('company', 'name', 'description')
        }),
        ('Permissions', {
            'fields': ('permissions',)
        }),
        ('Properties', {
            'fields': ('is_default', 'is_active', 'created_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'created_by')
    
    def created_by_display(self, obj):
        """Display who created the role"""
        if obj.created_by:
            return obj.created_by.full_name
        return '-'
    created_by_display.short_description = 'Created By'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """User activity admin interface"""
    list_display = [
        'user_display', 'activity_type', 'company',
        'description_short', 'ip_address', 'created_at'
    ]
    list_filter = ['activity_type', 'created_at']
    search_fields = [
        'user__full_name', 'user__email', 'description',
        'company__name', 'ip_address'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'company', 'activity_type', 'description')
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Context', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'company')
    
    def user_display(self, obj):
        """Display user name"""
        if obj.user:
            return obj.user.full_name
        return 'System'
    user_display.short_description = 'User'
    
    def description_short(self, obj):
        """Display shortened description"""
        if len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description
    description_short.short_description = 'Description'
    
    def has_add_permission(self, request):
        """Disable manual creation"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing"""
        return False


@admin.register(TeamCollaboration)
class TeamCollaborationAdmin(admin.ModelAdmin):
    """Team collaboration admin interface"""
    list_display = [
        'title', 'company', 'collaboration_type',
        'owner_display', 'participants_count', 'is_active', 'updated_at'
    ]
    list_filter = ['collaboration_type', 'is_active', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'company__name', 'owner__full_name']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Collaboration Information', {
            'fields': ('company', 'collaboration_type', 'title', 'description')
        }),
        ('Ownership', {
            'fields': ('owner',)
        }),
        ('Related Objects', {
            'fields': ('related_task', 'related_assessment', 'related_report'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active', 'is_public', 'settings')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'owner'
        ).prefetch_related('participants')
    
    def owner_display(self, obj):
        """Display collaboration owner"""
        if obj.owner:
            return obj.owner.full_name
        return '-'
    owner_display.short_description = 'Owner'
    
    def participants_count(self, obj):
        """Display number of participants"""
        count = obj.participants.count()
        return f"{count} participants"
    participants_count.short_description = 'Participants'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """User session admin interface"""
    list_display = [
        'user_display', 'ip_address', 'device_type',
        'browser', 'started_at', 'duration_display', 'is_active'
    ]
    list_filter = ['is_active', 'device_type', 'browser', 'started_at']
    search_fields = [
        'user__full_name', 'user__email', 'ip_address',
        'device_type', 'browser', 'location'
    ]
    ordering = ['-started_at']
    readonly_fields = [
        'session_key', 'started_at', 'last_activity',
        'ended_at', 'duration_seconds'
    ]
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'session_key', 'is_active')
        }),
        ('Device & Browser', {
            'fields': ('ip_address', 'user_agent', 'device_type', 'browser', 'location')
        }),
        ('Timeline', {
            'fields': ('started_at', 'last_activity', 'ended_at', 'duration_seconds')
        })
    )
    
    actions = ['end_sessions']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def user_display(self, obj):
        """Display user name"""
        if obj.user:
            return obj.user.full_name
        return '-'
    user_display.short_description = 'User'
    
    def duration_display(self, obj):
        """Display session duration"""
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
    duration_display.short_description = 'Duration'
    
    def end_sessions(self, request, queryset):
        """End selected active sessions"""
        active_sessions = queryset.filter(is_active=True)
        
        for session in active_sessions:
            session.end_session()
        
        self.message_user(
            request,
            f"Ended {active_sessions.count()} active sessions."
        )
    end_sessions.short_description = "End selected sessions"
    
    def has_add_permission(self, request):
        """Disable manual creation"""
        return False


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    """Company settings admin interface"""
    list_display = [
        'company', 'allow_self_registration', 'require_2fa',
        'max_team_size', 'updated_at'
    ]
    list_filter = [
        'allow_self_registration', 'require_email_verification',
        'require_2fa', 'allow_external_sharing'
    ]
    search_fields = ['company__name', 'admin_notification_email']
    ordering = ['company__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Company', {
            'fields': ('company',)
        }),
        ('User Registration', {
            'fields': (
                'allow_self_registration', 'require_email_verification',
                'default_user_role'
            )
        }),
        ('Security Settings', {
            'fields': (
                'password_expiry_days', 'require_2fa',
                'session_timeout_hours'
            )
        }),
        ('Collaboration', {
            'fields': ('allow_external_sharing', 'max_team_size')
        }),
        ('Notifications', {
            'fields': (
                'admin_notification_email', 'notify_on_new_user',
                'notify_on_role_change'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')


# Inline admin classes

class UserProfileInline(admin.StackedInline):
    """Inline for user profiles"""
    model = UserProfile
    extra = 0
    readonly_fields = ['last_activity', 'total_tasks_completed', 'total_reports_generated']


class TeamInvitationInline(admin.TabularInline):
    """Inline for team invitations"""
    model = TeamInvitation
    extra = 0
    readonly_fields = ['status', 'created_at', 'responded_at']
    fields = ['email', 'role', 'status', 'created_at', 'responded_at']


class UserActivityInline(admin.TabularInline):
    """Inline for user activities"""
    model = UserActivity
    extra = 0
    readonly_fields = ['activity_type', 'description', 'created_at']
    fields = ['activity_type', 'description', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False