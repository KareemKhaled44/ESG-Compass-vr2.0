# ESG Platform Django Backend

A comprehensive Django REST API backend for the ESG (Environmental, Social, Governance) platform, designed to perfectly match and support the frontend functionality.

## 📋 Overview

This backend provides a complete ESG management solution with features for:
- User authentication and team management
- Company onboarding and data management
- ESG assessments and compliance frameworks
- Task management and progress tracking
- Report generation (PDF/Excel)
- Dashboard analytics and metrics
- Team collaboration tools

## 🏗️ Project Structure

```
backend/
├── esg_platform/           # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI configuration
├── apps/                  # Django applications
│   ├── authentication/    # User auth & JWT
│   ├── companies/         # Company & location models
│   ├── esg_assessment/    # ESG frameworks & assessments
│   ├── tasks/            # Task management system
│   ├── reports/          # Report generation
│   ├── dashboard/        # Dashboard metrics & analytics
│   └── user_management/  # Team collaboration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🚀 Key Features

### Authentication System
- JWT-based authentication
- Custom User model with company association
- Role-based access control (Admin, Manager, Contributor, Viewer)
- Password reset and email verification

### Company Management
- Multi-company support
- Location management with UAE focus
- Business sector categorization
- Company settings and preferences

### ESG Assessment Framework
- Support for multiple frameworks (DST, Green Key, UAE Federal Climate Law)
- Dynamic question system with conditional logic
- Evidence attachment and verification
- Progress tracking and scoring
- Historical data management

### Task Management
- Task templates and categories
- Assignment and progress tracking
- Deadline management with notifications
- Comment system and attachments
- Recurring task support

### Report Generation
- PDF report generation using ReportLab
- Excel export capabilities
- Multiple report templates (ESG Comprehensive, DST, Green Key)
- Scheduled report generation
- Report sharing and access control

### Dashboard Analytics
- Real-time ESG score tracking
- Trend analysis and charts
- Progress indicators
- Alert system
- Benchmark comparisons
- KPI tracking

### User Management & Collaboration
- Team invitation system
- User profiles and activity tracking
- Role management
- Collaboration workspaces
- Session monitoring
- Company-specific settings

## 🔧 Technical Stack

- **Framework**: Django 4.2+ with Django REST Framework
- **Authentication**: JWT using djangorestframework-simplejwt
- **Database**: PostgreSQL (configurable)
- **File Storage**: Django file handling with pillow for images
- **Report Generation**: ReportLab (PDF), openpyxl (Excel)
- **Task Queue**: Celery with Redis (configured but optional)
- **CORS**: django-cors-headers for frontend integration

## 📊 Database Models

### Core Models
- **User**: Custom user model with company association
- **Company**: Business entity with ESG scoring
- **Location**: Company locations with UAE-specific fields
- **UserProfile**: Extended user information and preferences

### ESG Assessment
- **ESGAssessment**: Assessment instances for companies
- **ESGQuestion**: Dynamic question framework
- **ESGResponse**: User responses with evidence
- **ComplianceFramework**: Framework definitions (DST, Green Key, etc.)

### Task Management
- **Task**: Individual tasks with assignments
- **TaskTemplate**: Reusable task templates
- **TaskComment**: Collaboration and updates
- **TaskAttachment**: File attachments

### Reporting
- **ReportTemplate**: Report template definitions
- **GeneratedReport**: Generated report instances
- **ReportSection**: Template section configurations
- **ReportSchedule**: Automated report scheduling

### Dashboard & Analytics
- **DashboardMetric**: Calculated dashboard metrics
- **DashboardWidget**: Customizable dashboard widgets
- **DashboardAlert**: System alerts and notifications
- **BenchmarkData**: Industry benchmark data
- **AnalyticsEvent**: User interaction tracking

### Team Management
- **TeamInvitation**: Team member invitations
- **UserActivity**: Activity audit trail
- **TeamCollaboration**: Shared workspaces
- **UserSession**: Session tracking for security

## 🔗 API Endpoints

### Authentication (`/api/auth/`)
- `POST /login/` - User login
- `POST /register/` - User registration
- `POST /refresh/` - Token refresh
- `POST /demo-request/` - Demo account request

### Companies (`/api/companies/`)
- `GET /` - List companies
- `POST /` - Create company
- `GET /{id}/` - Company details
- `GET /locations/` - Company locations

### ESG Assessment (`/api/esg/`)
- `GET /assessments/` - List assessments
- `POST /assessments/` - Create assessment
- `GET /frameworks/` - Available frameworks
- `POST /responses/` - Submit responses

### Tasks (`/api/tasks/`)
- `GET /` - List tasks
- `POST /` - Create task
- `GET /{id}/` - Task details
- `POST /{id}/comments/` - Add comment

### Reports (`/api/reports/`)
- `GET /templates/` - Report templates
- `POST /generate/` - Generate report
- `GET /` - List reports
- `GET /{id}/download/` - Download report

### Dashboard (`/api/dashboard/`)
- `GET /overview/` - Dashboard overview
- `GET /metrics/` - Dashboard metrics
- `GET /trends/` - ESG trends
- `GET /alerts/` - System alerts

### User Management (`/api/users/`)
- `GET /team/overview/` - Team overview
- `GET /team/members/` - Team members
- `POST /invitations/` - Send invitations
- `GET /profile/` - User profile

## 🎯 Frontend Integration

This backend is specifically designed to match the frontend HTML structure:

### Dashboard (`dash.html`)
- **Overview endpoint** provides ESG scores, trends, and activity
- **Chart data** for Highcharts integration
- **Progress indicators** for completion tracking
- **Alert system** for notifications

### Task Tracker (`tracker.html`)
- **Progress tracking** with category breakdowns
- **Next steps** and task recommendations
- **Data completion** percentages

### Reports Hub (`report.html`)
- **Multiple report types** (ESG, DST, Green Key, Custom Export)
- **Report history** and access tracking
- **Scheduled reports** management

### Onboarding (`onboard.html`)
- **Multi-step wizard** support
- **Business information** collection
- **ESG scoping** configuration

## 🔒 Security Features

- JWT token authentication
- Role-based access control
- CORS configuration for frontend
- Input validation and sanitization
- Activity logging and audit trails
- Session management and monitoring
- File upload security

## 📱 Admin Interface

Comprehensive Django admin interface for:
- User management and permissions
- Company and location administration
- ESG framework configuration
- Task template management
- Report template design
- System monitoring and analytics

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

5. **Access Admin Panel**
   - URL: `http://localhost:8000/admin/`
   - Use superuser credentials

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend Integration
The backend is configured to work with the frontend at:
- Development: `http://localhost:3000`
- Production: Configure `CORS_ALLOWED_ORIGINS`

## 📈 Scalability Features

- Efficient database indexing
- Optimized querysets with select_related/prefetch_related
- Caching support (Redis configured)
- File storage abstraction
- Background task processing (Celery)
- API pagination and filtering
- Comprehensive logging

## 🧪 Testing

The backend includes comprehensive admin interfaces and is designed for easy testing:
- Django admin for data management
- API endpoints for frontend integration
- Serializer validation
- Model constraints and validation

## 📚 Documentation

- **API Documentation**: Available through Django REST Framework browsable API
- **Admin Documentation**: Built-in Django admin documentation
- **Model Documentation**: Comprehensive docstrings in models
- **Code Comments**: Detailed inline documentation

## 🤝 Contributing

This backend is designed to be:
- **Maintainable**: Clear code structure and documentation
- **Extensible**: Modular app design
- **Secure**: Best practices implemented
- **Performant**: Optimized queries and caching

## 📞 Support

For questions or issues:
1. Check the Django admin interface
2. Review API endpoint documentation
3. Examine model relationships
4. Check the comprehensive logging system

---

**Built with Django & Django REST Framework**  
*A complete ESG management solution backend*