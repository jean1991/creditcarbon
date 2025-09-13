# DRC Climate Action Reporting Platform

A comprehensive platform for climate action reporting in the Democratic Republic of Congo (DRC), featuring satellite data integration, secure user management, and ministry-approved document generation.

## Features

- **Satellite Data Integration**: Real-time forest loss monitoring using Global Forest Watch API
- **Province Mapping**: Complete mapping of DRC provinces with administrative codes
- **User Management**: Secure Flask-SQLAlchemy based authentication and authorization
- **File Upload**: Secure file upload system for climate data
- **Report Generation**: Enhanced PDF and Word document export with ministry branding
- **Chart Integration**: Automatic chart generation and inclusion in reports
- **Ministry Branding**: Official logo and signature integration in all exports

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jean1991/creditcarbon.git
   cd creditcarbon
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional):
   ```bash
   # Create .env file
   echo "SECRET_KEY=your-secret-key-here" > .env
   echo "DATABASE_URL=sqlite:///drc_climate.db" >> .env
   echo "GFW_API_KEY=your-global-forest-watch-api-key" >> .env
   ```

### Running the Application

1. **Start the Flask application**:
   ```bash
   python auth_upload_app.py
   ```

2. **Access the application**:
   - Open your web browser and navigate to `http://localhost:5000`
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123`

## Usage Guide

### 1. User Registration and Authentication

#### Register a New User
- Navigate to `/register`
- Fill in required information:
  - Username (unique)
  - Email address (unique)
  - Password
  - First and Last Name
  - Organization (optional)
- Users are created with 'user' role by default

#### Login
- Navigate to `/login`
- Enter username and password
- Successfully authenticated users are redirected to the dashboard

### 2. File Upload System

#### Supported File Types
- Text files (.txt)
- PDF documents (.pdf)
- Excel files (.xlsx, .xls)
- CSV files (.csv)
- JSON files (.json)
- XML files (.xml)

#### Upload Process
1. Go to Dashboard → "Upload Data File"
2. Select file (max 16MB)
3. Choose file type:
   - General Data
   - Satellite Data
   - Emission Data
   - Forest Data
   - Carbon Credit Data
4. Select applicable DRC province
5. Click "Upload File"

### 3. Satellite Data Integration

#### Available Provinces
The platform supports all 29 DRC provinces with correct admin codes:
- Original provinces: Kinshasa, Bas-Congo, Bandundu, Équateur, etc.
- New provinces (post-2015): Kongo Central, Kwango, Kwilu, etc.

#### Access Satellite Data
1. Go to Dashboard → "View Satellite Data"
2. Select province from dropdown
3. View forest loss data from Global Forest Watch
4. Data includes yearly forest loss in hectares

#### API Endpoints
- `GET /api/provinces` - List all available provinces
- `GET /api/satellite-data/<province>` - Get satellite data for specific province

### 4. Report Management

#### Create a Report
1. Go to Dashboard → "Create New Report"
2. Fill in report details:
   - Title
   - Description
   - Report Type (Forest Loss, Emission Inventory, etc.)
   - Province (optional)
3. Click "Create Report"

#### View Reports
- Go to Dashboard → "View All Reports"
- Click on any report title to view details
- Reports show metadata, status, and creation date

#### Export Reports
Reports can be exported in two formats:
- **PDF**: Professional layout with charts and branding
- **Word Document**: Editable format for further customization

Export features:
- Ministry logo inclusion
- Authorized signature placement
- Chart generation and embedding
- Professional formatting
- Metadata tables

### 5. Advanced Features

#### Chart Generation
The platform automatically generates charts from data:
- Line charts for trend analysis
- Bar charts for categorical data
- Pie charts for proportional data

#### Ministry Branding
All exports include:
- Official ministry logo (`logo.png`)
- Authorized signature placeholder (`signature.png`)
- Professional DRC government formatting

## File Structure

```
creditcarbon/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── logo.png                 # Ministry logo
├── signature.png            # Signature placeholder
├── main.py                  # Original blockchain demo
├── blockchain.py            # Blockchain implementation
├── identity.py              # Identity management
├── satellite_api.py         # Satellite data integration
├── models.py                # Database models (SQLAlchemy)
├── auth_upload_app.py       # Main Flask application
├── export_enhanced.py       # Report export functionality
├── uploads/                 # File upload directory
└── exports/                 # Generated report exports
```

## API Reference

### Authentication Endpoints

- `POST /register` - Register new user
- `POST /login` - User login
- `GET /logout` - User logout

### File Management

- `POST /upload` - Upload data file
- `GET /upload` - File upload form

### Report Management

- `GET /reports` - List user reports
- `POST /reports/create` - Create new report
- `GET /reports/<id>` - View specific report
- `GET /reports/<id>/export` - Export report

### Satellite Data

- `GET /satellite-data` - Satellite data interface
- `GET /api/provinces` - List DRC provinces
- `GET /api/satellite-data/<province>` - Get province data

## Database Schema

### Users Table
- id, uuid, username, email, password_hash
- first_name, last_name, organization, role
- is_active, is_verified, created_at, last_login

### File Uploads Table
- id, uuid, filename, original_filename, file_path
- file_size, mime_type, file_type, province
- upload_date, processed, processing_status, metadata

### Reports Table
- id, uuid, title, description, report_type
- province, reporting_period_start, reporting_period_end
- status, created_at, updated_at, data, charts_config

### Report Exports Table
- id, uuid, export_format, filename, file_path
- file_size, export_date, includes_charts, includes_logo
- includes_signature, export_settings

## Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_URL`: Database connection string
- `GFW_API_KEY`: Global Forest Watch API key (optional)
- `UPLOAD_FOLDER`: Directory for file uploads (default: 'uploads')
- `MAX_CONTENT_LENGTH`: Maximum file size (default: 16MB)

### Default Settings

- Database: SQLite (drc_climate.db)
- File uploads: 16MB maximum
- Supported formats: txt, pdf, csv, xlsx, xls, json, xml
- Default admin user: admin/admin123

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 auth_upload_app:app
```

### Environment Setup

1. Set strong `SECRET_KEY`
2. Use production database (PostgreSQL recommended)
3. Configure proper file storage
4. Set up HTTPS/SSL
5. Configure firewall and security groups

### Database Migration

For production, consider using Flask-Migrate:

```bash
pip install Flask-Migrate
```

## Security Considerations

- Passwords are hashed using Werkzeug's security utilities
- File uploads are restricted by type and size
- User sessions are managed securely
- SQL injection protection via SQLAlchemy ORM
- CSRF protection recommended for production

## Global Forest Watch Integration

### Province Mapping
The platform includes complete mapping of DRC provinces to Global Forest Watch administrative codes:

```python
# Example: Kinshasa Province
"Kinshasa": ("CD-KN", "CD.1")
# admin_code: CD-KN (ISO 3166-2)
# gfw_admin_id: CD.1 (Global Forest Watch)
```

### Data Sources
- University of Maryland Tree Cover Loss dataset
- FIRMS/MODIS fire detection data
- Real-time and historical satellite imagery

## Troubleshooting

### Common Issues

1. **ImportError for PDF/Word export**:
   ```bash
   pip install reportlab python-docx matplotlib
   ```

2. **Database not found**:
   - Ensure SQLite database is created automatically on first run
   - Check file permissions in application directory

3. **File upload fails**:
   - Check file size (max 16MB)
   - Verify file type is in allowed extensions
   - Ensure uploads/ directory exists and is writable

4. **Satellite API errors**:
   - API returns mock data when external service unavailable
   - Check internet connectivity for real data
   - Verify Global Forest Watch API key if using real API

### Debug Mode

Run application in debug mode for development:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is developed for the Democratic Republic of Congo Ministry of Environment and Sustainable Development.

## Support

For technical support or questions about the DRC Climate Action Reporting Platform, please contact the development team or create an issue in the repository.