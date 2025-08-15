# ESG Compass v2 🌍

A comprehensive Environmental, Social, and Governance (ESG) compliance platform designed for UAE SMEs to track, manage, and report on their sustainability initiatives.

## 🚀 Features

### 📊 **Smart Dashboard**
- Real-time ESG metrics visualization
- Interactive charts and progress tracking
- File-based data analysis and scoring
- Multi-category performance insights

### 📈 **Progress Tracker**
- Separate tracking for data entry vs evidence uploads
- Database-driven completion status
- Category-based progress breakdown (Environmental, Social, Governance)
- Smart task categorization and file counting

### 📋 **Task Management**
- Dynamic task generation based on company profile
- Evidence upload with file type validation
- Progress monitoring and completion tracking
- Flexible evidence submission (data entry OR file upload)

### 📑 **Comprehensive Reporting**
- PDF report generation with multiple templates
- Dubai Sustainable Tourism (DST) compliance reports
- Green Key Certification assessments
- Custom ESG comprehensive reports

### 🏢 **Company Onboarding**
- ESG scoping wizard for initial setup
- Sector-specific task generation
- Location and business type configuration
- Automated compliance framework assignment

### 🔐 **Authentication & Security**
- Secure user authentication
- Company-based data isolation
- Role-based access control
- Session management

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **React Query** - Data fetching and caching
- **React Hook Form** - Form management
- **Recharts** - Data visualization

### Backend
- **Django 4.x** - Python web framework
- **Django REST Framework** - API development
- **SQLite** - Database (production-ready for SMEs)
- **ReportLab** - PDF generation
- **Python 3.12** - Core language

## 📦 Installation

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.12+
- **Git**

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend-react

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database
The application uses SQLite by default. For production, configure PostgreSQL or MySQL in `settings.py`.

## 📚 API Documentation

### Key Endpoints
- `POST /api/auth/login/` - User authentication
- `GET /api/tasks/` - Retrieve user tasks
- `POST /api/tasks/{id}/attachments/` - Upload evidence
- `GET /api/dashboard/overview/` - Dashboard metrics
- `GET /api/reports/` - Available reports
- `POST /api/reports/generate/` - Generate PDF reports

### Authentication
The API uses session-based authentication. Include session cookies with requests after login.

## 🎯 Usage

### For Companies
1. **Register** your company account
2. **Complete onboarding** with ESG scoping wizard
3. **Complete tasks** by uploading evidence or entering data
4. **Monitor progress** through the dashboard and tracker
5. **Generate reports** for compliance and stakeholders

### For Administrators
1. Access admin panel at `/admin`
2. Manage users, companies, and tasks
3. Monitor system health and data quality
4. Configure report templates and compliance frameworks

## 🌟 Key Differentiators

- **UAE-Specific**: Tailored for UAE SME compliance requirements
- **Flexible Evidence**: Support for both data entry and file uploads
- **Smart Categorization**: Automatic task type detection and validation
- **Real-time Tracking**: Database-driven progress monitoring
- **Comprehensive Reporting**: Multiple compliance frameworks supported

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
python manage.py test
```

### Run Frontend Tests
```bash
cd frontend-react
npm test
```

## 📱 Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 📧 Support

For support and inquiries, please contact the development team.

## 🎯 Roadmap

- [ ] Multi-language support (Arabic/English)
- [ ] Mobile application
- [ ] Advanced analytics and benchmarking
- [ ] Third-party integrations (ADDC, DEWA)
- [ ] Automated compliance monitoring
- [ ] AI-powered recommendations

---

**Built with ❤️ for sustainable business practices in the UAE**

🎯 *Generated with [Claude Code](https://claude.ai/code)*