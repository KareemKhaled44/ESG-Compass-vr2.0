from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
from collections import defaultdict

from .models import (
    TeamInvitation, UserProfile, TeamRole, UserActivity,
    TeamCollaboration, CollaborationParticipant, UserSession, CompanySettings
)
from .serializers import (
    UserProfileSerializer, TeamMemberSerializer, TeamInvitationSerializer,
    CreateInvitationSerializer, TeamRoleSerializer, UserActivitySerializer,
    TeamCollaborationSerializer, CollaborationParticipantSerializer,
    UserSessionSerializer, CompanySettingsSerializer, TeamStatisticsSerializer,
    UserPermissionsSerializer, InviteAcceptSerializer, BulkInviteSerializer,
    TeamOverviewSerializer, RoleUpdateSerializer
)

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_overview(request):
    """
    Get team overview with statistics and recent activity
    """
    company = request.user.company
    if not company:
        return Response(
            {'error': 'User not associated with a company'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Team statistics
    team_stats = _get_team_statistics(company)
    
    # Recent members (last 5 joined)
    recent_members = User.objects.filter(
        company=company
    ).order_by('-date_joined')[:5]
    
    # Pending invitations
    pending_invitations = TeamInvitation.objects.filter(
        company=company,
        status='pending'
    ).order_by('-created_at')[:5]
    
    # Recent activities
    recent_activities = UserActivity.objects.filter(
        company=company
    ).order_by('-created_at')[:10]
    
    # Active sessions
    active_sessions = UserSession.objects.filter(
        user__company=company,
        is_active=True
    ).order_by('-last_activity')[:10]
    
    overview_data = {
        'team_statistics': team_stats,
        'recent_members': recent_members,
        'pending_invitations': pending_invitations,
        'recent_activities': recent_activities,
        'active_sessions': active_sessions
    }
    
    serializer = TeamOverviewSerializer(overview_data)
    return Response(serializer.data)


class TeamMemberListView(generics.ListAPIView):
    """List all team members"""
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        company = self.request.user.company
        return User.objects.filter(
            company=company
        ).select_related('profile').order_by('full_name')


class TeamMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or remove a team member"""
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(company=self.request.user.company)
    
    def destroy(self, request, *args, **kwargs):
        """Remove team member (soft delete)"""
        instance = self.get_object()
        
        # Prevent self-deletion
        if instance == request.user:
            return Response(
                {'error': 'Cannot remove yourself from the team'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions (only admins can remove users)
        if request.user.role != 'admin':
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete - remove company association
        instance.company = None
        instance.is_active = False
        instance.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            company=request.user.company,
            activity_type='team_removed',
            description=f'Removed {instance.full_name} from team',
            metadata={'removed_user_id': str(instance.id)}
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class TeamInvitationListView(generics.ListCreateAPIView):
    """List and create team invitations"""
    serializer_class = TeamInvitationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TeamInvitation.objects.filter(
            company=self.request.user.company
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateInvitationSerializer
        return TeamInvitationSerializer
    
    def perform_create(self, serializer):
        invitation = serializer.save()
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            company=self.request.user.company,
            activity_type='team_invited',
            description=f'Invited {invitation.email} to join team',
            metadata={'invitation_id': str(invitation.id)}
        )
        
        # TODO: Send invitation email
        # send_invitation_email(invitation)


class TeamInvitationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage individual team invitations"""
    serializer_class = TeamInvitationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TeamInvitation.objects.filter(
            company=self.request.user.company
        )
    
    def destroy(self, request, *args, **kwargs):
        """Cancel invitation"""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response(
                {'error': 'Can only cancel pending invitations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invitation.cancel()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def accept_invitation(request):
    """Accept team invitation and create user account"""
    serializer = InviteAcceptSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        return Response({
            'message': 'Invitation accepted successfully',
            'user_id': user.id,
            'company': user.company.name
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_invitation(request, invitation_id):
    """Resend team invitation"""
    try:
        invitation = TeamInvitation.objects.get(
            id=invitation_id,
            company=request.user.company,
            status='pending'
        )
        
        if invitation.is_expired:
            # Extend expiry
            invitation.expires_at = timezone.now() + timedelta(days=7)
            invitation.save()
        
        # TODO: Send invitation email
        # send_invitation_email(invitation)
        
        return Response({'message': 'Invitation resent successfully'})
        
    except TeamInvitation.DoesNotExist:
        return Response(
            {'error': 'Invitation not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_invite(request):
    """Send bulk invitations"""
    serializer = BulkInviteSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        invitations = serializer.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            company=request.user.company,
            activity_type='bulk_invite',
            description=f'Sent {len(invitations)} bulk invitations',
            metadata={'invitation_count': len(invitations)}
        )
        
        return Response({
            'message': f'Successfully sent {len(invitations)} invitations',
            'invitations': TeamInvitationSerializer(invitations, many=True).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_role(request):
    """Update user role"""
    serializer = RoleUpdateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.user
        old_role = user.role
        new_role = serializer.validated_data['new_role']
        
        user.role = new_role
        user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            company=request.user.company,
            activity_type='role_changed',
            description=f'Changed {user.full_name} role from {old_role} to {new_role}',
            metadata={
                'target_user_id': str(user.id),
                'old_role': old_role,
                'new_role': new_role
            }
        )
        
        return Response({
            'message': 'User role updated successfully',
            'user': TeamMemberSerializer(user).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions(request):
    """Get current user's permissions"""
    user = request.user
    
    permissions = {
        'can_invite_users': user.role in ['admin', 'manager'],
        'can_manage_roles': user.role == 'admin',
        'can_view_reports': user.role in ['admin', 'manager', 'contributor'],
        'can_manage_assessments': user.role in ['admin', 'manager'],
        'can_export_data': user.role in ['admin', 'manager'],
        'can_manage_settings': user.role == 'admin',
        'can_delete_users': user.role == 'admin',
        'can_assign_tasks': user.role in ['admin', 'manager'],
    }
    
    serializer = UserPermissionsSerializer(permissions)
    return Response(serializer.data)


class UserActivityListView(generics.ListAPIView):
    """List user activities with filtering"""
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = UserActivity.objects.filter(
            company=self.request.user.company
        ).select_related('user').order_by('-created_at')
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by activity type
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset


class TeamCollaborationListView(generics.ListCreateAPIView):
    """List and create team collaborations"""
    serializer_class = TeamCollaborationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TeamCollaboration.objects.filter(
            company=self.request.user.company,
            is_active=True
        ).order_by('-updated_at')
    
    def perform_create(self, serializer):
        serializer.save(
            company=self.request.user.company,
            owner=self.request.user
        )


class UserSessionListView(generics.ListAPIView):
    """List user sessions for monitoring"""
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only admins can view all sessions
        if self.request.user.role == 'admin':
            return UserSession.objects.filter(
                user__company=self.request.user.company
            ).select_related('user').order_by('-started_at')
        else:
            # Users can only see their own sessions
            return UserSession.objects.filter(
                user=self.request.user
            ).order_by('-started_at')


class CompanySettingsView(generics.RetrieveUpdateAPIView):
    """Get and update company user management settings"""
    serializer_class = CompanySettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        company = self.request.user.company
        settings, created = CompanySettings.objects.get_or_create(
            company=company
        )
        return settings
    
    def update(self, request, *args, **kwargs):
        # Only admins can update settings
        if request.user.role != 'admin':
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_statistics(request):
    """Get detailed team statistics"""
    company = request.user.company
    if not company:
        return Response(
            {'error': 'User not associated with a company'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    stats = _get_team_statistics(company)
    serializer = TeamStatisticsSerializer(stats)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_user_activity(request):
    """Track user activity"""
    activity_data = request.data
    
    UserActivity.objects.create(
        user=request.user,
        company=request.user.company,
        activity_type=activity_data.get('activity_type'),
        description=activity_data.get('description', ''),
        metadata=activity_data.get('metadata', {}),
        ip_address=_get_client_ip(request)
    )
    
    return Response({'message': 'Activity tracked successfully'})


# Helper functions

def _get_team_statistics(company):
    """Calculate team statistics"""
    total_members = User.objects.filter(company=company).count()
    active_members = User.objects.filter(company=company, is_active=True).count()
    pending_invitations = TeamInvitation.objects.filter(
        company=company,
        status='pending'
    ).count()
    
    # Role distribution
    roles_data = User.objects.filter(company=company).values('role').annotate(
        count=Count('id')
    )
    roles_distribution = {item['role']: item['count'] for item in roles_data}
    
    # Department distribution
    dept_data = UserProfile.objects.filter(
        user__company=company
    ).values('department').annotate(count=Count('id'))
    department_distribution = {item['department'] or 'Not specified': item['count'] for item in dept_data}
    
    # Recent activity count (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_activity_count = UserActivity.objects.filter(
        company=company,
        created_at__gte=week_ago
    ).count()
    
    # Average session duration
    completed_sessions = UserSession.objects.filter(
        user__company=company,
        is_active=False,
        duration_seconds__gt=0
    )
    avg_session_duration = completed_sessions.aggregate(
        avg_duration=Avg('duration_seconds')
    )['avg_duration'] or 0
    
    # Monthly metrics
    month_ago = timezone.now() - timedelta(days=30)
    
    # Mock data for now - would be calculated from actual task/report data
    tasks_completed_this_month = 45
    reports_generated_this_month = 12
    assessments_completed_this_month = 8
    
    # Collaboration metrics
    active_collaborations = TeamCollaboration.objects.filter(
        company=company,
        is_active=True
    ).count()
    total_collaborations = TeamCollaboration.objects.filter(
        company=company
    ).count()
    
    return {
        'total_members': total_members,
        'active_members': active_members,
        'pending_invitations': pending_invitations,
        'roles_distribution': roles_distribution,
        'department_distribution': department_distribution,
        'recent_activity_count': recent_activity_count,
        'average_session_duration': avg_session_duration / 3600,  # Convert to hours
        'tasks_completed_this_month': tasks_completed_this_month,
        'reports_generated_this_month': reports_generated_this_month,
        'assessments_completed_this_month': assessments_completed_this_month,
        'active_collaborations': active_collaborations,
        'total_collaborations': total_collaborations,
    }


def _get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip