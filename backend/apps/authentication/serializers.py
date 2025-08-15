from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from .models import User
from apps.companies.models import Company


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data - matches frontend expectations"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_id = serializers.CharField(source='company.id', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role', 'company_id', 'company_name',
            'phone_number', 'job_title', 'department', 'is_verified', 
            'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']


class RegisterSerializer(serializers.Serializer):
    """
    Registration serializer matching signup.html form fields:
    - Full Name
    - Email Address  
    - Company Name
    - Company Description (optional)
    - Main Location (optional)
    - Business Sector
    - Password
    - Confirm Password
    """
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    company_name = serializers.CharField(max_length=255)
    company_description = serializers.CharField(required=False, allow_blank=True)
    main_location = serializers.CharField(max_length=255, required=False, default='Dubai, UAE')
    business_sector = serializers.ChoiceField(choices=[
        ('hospitality', 'Hospitality & Tourism'),
        ('construction', 'Construction & Real Estate'),
        ('manufacturing', 'Manufacturing'),
        ('logistics', 'Logistics & Transportation'),
        ('education', 'Education'),
        ('healthcare', 'Healthcare'),
        ('retail', 'Retail & E-commerce'),
        ('technology', 'Technology & Software')
    ])
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_password(self, value):
        """Validate password strength"""
        validate_password(value)
        return value
    
    def validate(self, attrs):
        """Check that passwords match"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        """Create user and company"""
        # Remove confirm_password from validated_data
        validated_data.pop('confirm_password')
        
        # Extract company data
        company_name = validated_data.pop('company_name')
        company_description = validated_data.pop('company_description', '')
        main_location = validated_data.pop('main_location')
        business_sector = validated_data.pop('business_sector')
        
        # Create company first
        company = Company.objects.create(
            name=company_name,
            description=company_description,
            business_sector=business_sector,
            main_location=main_location
        )
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],  # Use email as username
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            company=company,
            role='admin',        # Default role is admin
            department='Management',  # Default department is Management
            is_active=True       # Ensure user is active by default
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Login serializer matching login.html form fields:
    - Email Address (sent as 'username' from frontend)
    - Password
    """
    username = serializers.EmailField()  # Frontend sends email as username
    password = serializers.CharField()
    
    def validate(self, attrs):
        """Authenticate user"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Authenticate using email as username
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "username" and "password".')


class DemoRequestSerializer(serializers.Serializer):
    """
    Demo request serializer matching login.html demo form:
    - First Name, Last Name
    - Business Email
    - Company Name
    - Industry
    - Company Size
    """
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    business_email = serializers.EmailField()
    company_name = serializers.CharField(max_length=255)
    industry = serializers.ChoiceField(choices=[
        ('hospitality', 'Hospitality & Tourism'),
        ('construction', 'Construction & Real Estate'),
        ('logistics', 'Logistics & Transportation'),
        ('retail', 'Retail & Commerce'),
        ('manufacturing', 'Manufacturing'),
        ('other', 'Other')
    ])
    company_size = serializers.ChoiceField(choices=[
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees')
    ])
    marketing_consent = serializers.BooleanField(default=False)


class PasswordResetSerializer(serializers.Serializer):
    """Password reset request"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Check if user exists"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirmation"""
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField()
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Update user profile information"""
    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'job_title', 'department']
    
    def validate_full_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Full name cannot be empty.")
        return value