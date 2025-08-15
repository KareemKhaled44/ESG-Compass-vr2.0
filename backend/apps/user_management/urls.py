from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    # Team overview and statistics
    path('team/overview/', views.team_overview, name='team_overview'),
    path('team/statistics/', views.team_statistics, name='team_statistics'),
    
    # Team member management
    path('team/members/', views.TeamMemberListView.as_view(), name='team_members'),
    path('team/members/<uuid:pk>/', views.TeamMemberDetailView.as_view(), name='team_member_detail'),
    path('team/members/role/update/', views.update_user_role, name='update_user_role'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('permissions/', views.user_permissions, name='user_permissions'),
    
    # Team invitations
    path('invitations/', views.TeamInvitationListView.as_view(), name='team_invitations'),
    path('invitations/<uuid:pk>/', views.TeamInvitationDetailView.as_view(), name='invitation_detail'),
    path('invitations/<uuid:invitation_id>/resend/', views.resend_invitation, name='resend_invitation'),
    path('invitations/bulk/', views.bulk_invite, name='bulk_invite'),
    path('invitations/accept/', views.accept_invitation, name='accept_invitation'),
    
    # Activity tracking
    path('activities/', views.UserActivityListView.as_view(), name='user_activities'),
    path('activities/track/', views.track_user_activity, name='track_user_activity'),
    
    # Collaborations
    path('collaborations/', views.TeamCollaborationListView.as_view(), name='team_collaborations'),
    
    # Sessions monitoring
    path('sessions/', views.UserSessionListView.as_view(), name='user_sessions'),
    
    # Company settings
    path('settings/', views.CompanySettingsView.as_view(), name='company_settings'),
]