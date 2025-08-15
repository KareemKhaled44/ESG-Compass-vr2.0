#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/mnt/c/Users/20100/v3/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esg_platform.settings')
django.setup()

from apps.authentication.models import User
from apps.companies.models import Company

# Create test company
company = Company.objects.create(
    name='Test ESG Company',
    business_sector='technology'
)

# Create superuser
user = User.objects.create_user(
    username='admin',
    email='admin@test.com',
    password='admin123',
    full_name='Admin User'
)
user.company = company
user.role = 'admin'
user.is_staff = True
user.is_superuser = True
user.save()

print('Superuser created successfully!')
print('Email: admin@test.com')
print('Password: admin123')
print('Company:', company.name)