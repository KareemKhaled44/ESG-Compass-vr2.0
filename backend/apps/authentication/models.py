from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser
    Matches the frontend user structure from signup.html and login.html
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='Email Address')
    full_name = models.CharField(max_length=255, verbose_name='Full Name')
    
    # Company relationship (will be set after company creation)
    company = models.ForeignKey(
        'companies.Company', 
        on_delete=models.CASCADE, 
        related_name='users', 
        null=True, 
        blank=True
    )
    
    # User role within company
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('contributor', 'Contributor'),
        ('viewer', 'Viewer'),
    ]
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='contributor',
        help_text='User role within the company'
    )
    
    # Profile information
    phone_number = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # User preferences
    preferences = models.JSONField(default=dict, blank=True)
    
    # Make email the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    @property
    def is_company_admin(self):
        """Check if user is admin of their company"""
        return self.role == 'admin'
    
    @property
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role in ['admin', 'manager']
    
    def get_full_name(self):
        return self.full_name
    
    def get_short_name(self):
        return self.full_name.split(' ')[0] if self.full_name else self.email



class PasswordResetToken(models.Model):
    """Handle password reset functionality"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reset token for {self.user.email}"