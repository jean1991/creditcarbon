"""
Flask application for DRC climate action reporting platform.
Provides user authentication, file upload, and report management functionality.
"""

from flask import Flask, request, jsonify, render_template_string, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import json
from datetime import datetime, timedelta
import uuid

# Import our models and satellite API
from models import db, User, FileUpload, Report, ReportExport, init_db, create_admin_user, create_user
from satellite_api import SatelliteAPIClient

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///drc_climate.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'xlsx', 'xls', 'json', 'xml'}

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize database
init_db(app)

# Initialize satellite API client
satellite_client = SatelliteAPIClient()

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return User.query.get(int(user_id))

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        try:
            user = create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                organization=data.get('organization', ''),
                role=data.get('role', 'user')
            )
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'User registered successfully',
                    'user': user.to_dict()
                }), 201
            else:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
                
        except ValueError as e:
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 400
            else:
                flash(str(e), 'error')
    
    # Simple registration form
    registration_form = '''
    <!DOCTYPE html>
    <html>
    <head><title>Register - DRC Climate Platform</title></head>
    <body>
        <h2>Register for DRC Climate Action Platform</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}
        <form method="POST">
            <p><label>Username: <input type="text" name="username" required></label></p>
            <p><label>Email: <input type="email" name="email" required></label></p>
            <p><label>Password: <input type="password" name="password" required></label></p>
            <p><label>First Name: <input type="text" name="first_name" required></label></p>
            <p><label>Last Name: <input type="text" name="last_name" required></label></p>
            <p><label>Organization: <input type="text" name="organization"></label></p>
            <p><input type="submit" value="Register"></p>
        </form>
        <p><a href="{{ url_for('login') }}">Already have an account? Login here</a></p>
    </body>
    </html>
    '''
    return render_template_string(registration_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': user.to_dict()
                })
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            else:
                flash('Invalid username or password', 'error')
    
    # Simple login form
    login_form = '''
    <!DOCTYPE html>
    <html>
    <head><title>Login - DRC Climate Platform</title></head>
    <body>
        <h2>Login to DRC Climate Action Platform</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}
        <form method="POST">
            <p><label>Username: <input type="text" name="username" required></label></p>
            <p><label>Password: <input type="password" name="password" required></label></p>
            <p><input type="submit" value="Login"></p>
        </form>
        <p><a href="{{ url_for('register') }}">Don't have an account? Register here</a></p>
    </body>
    </html>
    '''
    return render_template_string(login_form)

@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Main application routes
@app.route('/')
def index():
    """Home page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    home_page = '''
    <!DOCTYPE html>
    <html>
    <head><title>DRC Climate Action Reporting Platform</title></head>
    <body>
        <h1>Democratic Republic of Congo Climate Action Reporting Platform</h1>
        <p>Welcome to the official climate action reporting platform for DRC.</p>
        <p>This platform provides:</p>
        <ul>
            <li>Satellite data integration for forest monitoring</li>
            <li>Carbon emission tracking and reporting</li>
            <li>Ministry-approved report generation</li>
            <li>Secure data management and user authentication</li>
        </ul>
        <p>
            <a href="{{ url_for('login') }}">Login</a> | 
            <a href="{{ url_for('register') }}">Register</a>
        </p>
    </body>
    </html>
    '''
    return render_template_string(home_page)

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    # Get user's recent uploads and reports
    recent_uploads = FileUpload.query.filter_by(user_id=current_user.id).order_by(FileUpload.upload_date.desc()).limit(5).all()
    recent_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).limit(5).all()
    
    dashboard_page = '''
    <!DOCTYPE html>
    <html>
    <head><title>Dashboard - DRC Climate Platform</title></head>
    <body>
        <h1>Welcome, {{ current_user.first_name }} {{ current_user.last_name }}</h1>
        <p>Organization: {{ current_user.organization or 'N/A' }}</p>
        <p>Role: {{ current_user.role }}</p>
        
        <h2>Quick Actions</h2>
        <ul>
            <li><a href="{{ url_for('upload_file') }}">Upload Data File</a></li>
            <li><a href="{{ url_for('create_report') }}">Create New Report</a></li>
            <li><a href="{{ url_for('satellite_data') }}">View Satellite Data</a></li>
            <li><a href="{{ url_for('list_reports') }}">View All Reports</a></li>
        </ul>
        
        <h3>Recent Uploads</h3>
        {% if recent_uploads %}
            <ul>
            {% for upload in recent_uploads %}
                <li>{{ upload.original_filename }} ({{ upload.upload_date.strftime('%Y-%m-%d %H:%M') }})</li>
            {% endfor %}
            </ul>
        {% else %}
            <p>No recent uploads</p>
        {% endif %}
        
        <h3>Recent Reports</h3>
        {% if recent_reports %}
            <ul>
            {% for report in recent_reports %}
                <li><a href="{{ url_for('view_report', report_id=report.id) }}">{{ report.title }}</a> ({{ report.created_at.strftime('%Y-%m-%d') }})</li>
            {% endfor %}
            </ul>
        {% else %}
            <p>No recent reports</p>
        {% endif %}
        
        <p><a href="{{ url_for('logout') }}">Logout</a></p>
    </body>
    </html>
    '''
    return render_template_string(dashboard_page, current_user=current_user, recent_uploads=recent_uploads, recent_reports=recent_reports)

# File upload routes
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """File upload interface."""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        file_type = request.form.get('file_type', 'general')
        province = request.form.get('province', '')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(file_path)
                file_size = os.path.getsize(file_path)
                
                # Create file upload record
                upload = FileUpload(
                    filename=filename,
                    original_filename=file.filename,
                    file_path=file_path,
                    file_size=file_size,
                    mime_type=file.content_type,
                    file_type=file_type,
                    province=province,
                    user_id=current_user.id
                )
                
                db.session.add(upload)
                db.session.commit()
                
                flash(f'File "{file.filename}" uploaded successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                flash(f'Error uploading file: {str(e)}', 'error')
        else:
            flash('Invalid file type. Allowed types: ' + ', '.join(app.config['ALLOWED_EXTENSIONS']), 'error')
    
    # Get list of DRC provinces for dropdown
    provinces = satellite_client.list_available_provinces()
    
    upload_form = '''
    <!DOCTYPE html>
    <html>
    <head><title>Upload File - DRC Climate Platform</title></head>
    <body>
        <h2>Upload Data File</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}
        <form method="POST" enctype="multipart/form-data">
            <p><label>File: <input type="file" name="file" required></label></p>
            <p><label>File Type: 
                <select name="file_type">
                    <option value="general">General Data</option>
                    <option value="satellite_data">Satellite Data</option>
                    <option value="emission_data">Emission Data</option>
                    <option value="forest_data">Forest Data</option>
                    <option value="carbon_data">Carbon Credit Data</option>
                </select>
            </label></p>
            <p><label>Province: 
                <select name="province">
                    <option value="">Select Province</option>
                    {% for province in provinces %}
                        <option value="{{ province }}">{{ province }}</option>
                    {% endfor %}
                </select>
            </label></p>
            <p><input type="submit" value="Upload File"></p>
        </form>
        <p><a href="{{ url_for('dashboard') }}">Back to Dashboard</a></p>
    </body>
    </html>
    '''
    return render_template_string(upload_form, provinces=provinces)

# Satellite data routes
@app.route('/satellite-data')
@login_required
def satellite_data():
    """View satellite data for DRC provinces."""
    province = request.args.get('province', 'Kinshasa')
    
    try:
        # Get forest loss data
        forest_data = satellite_client.get_forest_loss_data(province, (2020, 2023))
        data_json = json.dumps(forest_data, indent=2)
    except Exception as e:
        forest_data = None
        data_json = f"Error fetching data: {str(e)}"
    
    provinces = satellite_client.list_available_provinces()
    
    satellite_page = '''
    <!DOCTYPE html>
    <html>
    <head><title>Satellite Data - DRC Climate Platform</title></head>
    <body>
        <h2>Satellite Data for DRC Provinces</h2>
        <form method="GET">
            <label>Select Province: 
                <select name="province" onchange="this.form.submit()">
                    {% for prov in provinces %}
                        <option value="{{ prov }}" {% if prov == province %}selected{% endif %}>{{ prov }}</option>
                    {% endfor %}
                </select>
            </label>
        </form>
        
        <h3>Forest Loss Data for {{ province }}</h3>
        <pre>{{ data_json }}</pre>
        
        <p><a href="{{ url_for('dashboard') }}">Back to Dashboard</a></p>
    </body>
    </html>
    '''
    return render_template_string(satellite_page, provinces=provinces, province=province, data_json=data_json)

# Report management routes
@app.route('/reports')
@login_required
def list_reports():
    """List user's reports."""
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    
    reports_page = '''
    <!DOCTYPE html>
    <html>
    <head><title>Reports - DRC Climate Platform</title></head>
    <body>
        <h2>Your Reports</h2>
        <p><a href="{{ url_for('create_report') }}">Create New Report</a></p>
        
        {% if reports %}
            <table border="1">
                <tr>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Province</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
                {% for report in reports %}
                <tr>
                    <td>{{ report.title }}</td>
                    <td>{{ report.report_type }}</td>
                    <td>{{ report.province or 'N/A' }}</td>
                    <td>{{ report.status }}</td>
                    <td>{{ report.created_at.strftime('%Y-%m-%d') }}</td>
                    <td>
                        <a href="{{ url_for('view_report', report_id=report.id) }}">View</a> |
                        <a href="{{ url_for('export_report', report_id=report.id) }}">Export</a>
                    </td>
                </tr>
                {% endfor %}
            </table>
        {% else %}
            <p>No reports found. <a href="{{ url_for('create_report') }}">Create your first report</a></p>
        {% endif %}
        
        <p><a href="{{ url_for('dashboard') }}">Back to Dashboard</a></p>
    </body>
    </html>
    '''
    return render_template_string(reports_page, reports=reports)

@app.route('/reports/create', methods=['GET', 'POST'])
@login_required
def create_report():
    """Create a new report."""
    if request.method == 'POST':
        data = request.form
        
        report = Report(
            title=data['title'],
            description=data.get('description', ''),
            report_type=data['report_type'],
            province=data.get('province', ''),
            user_id=current_user.id
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Report created successfully!', 'success')
        return redirect(url_for('view_report', report_id=report.id))
    
    provinces = satellite_client.list_available_provinces()
    
    create_form = '''
    <!DOCTYPE html>
    <html>
    <head><title>Create Report - DRC Climate Platform</title></head>
    <body>
        <h2>Create New Report</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}
        <form method="POST">
            <p><label>Title: <input type="text" name="title" required style="width: 300px;"></label></p>
            <p><label>Description: <textarea name="description" rows="3" style="width: 300px;"></textarea></label></p>
            <p><label>Report Type: 
                <select name="report_type" required>
                    <option value="forest_loss">Forest Loss Assessment</option>
                    <option value="emission_inventory">Emission Inventory</option>
                    <option value="carbon_credit">Carbon Credit Report</option>
                    <option value="climate_action">Climate Action Report</option>
                </select>
            </label></p>
            <p><label>Province: 
                <select name="province">
                    <option value="">All Provinces</option>
                    {% for province in provinces %}
                        <option value="{{ province }}">{{ province }}</option>
                    {% endfor %}
                </select>
            </label></p>
            <p><input type="submit" value="Create Report"></p>
        </form>
        <p><a href="{{ url_for('list_reports') }}">Back to Reports</a></p>
    </body>
    </html>
    '''
    return render_template_string(create_form, provinces=provinces)

@app.route('/reports/<int:report_id>')
@login_required
def view_report(report_id):
    """View a specific report."""
    report = Report.query.get_or_404(report_id)
    
    # Check if user owns the report or is admin
    if report.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('list_reports'))
    
    report_page = '''
    <!DOCTYPE html>
    <html>
    <head><title>{{ report.title }} - DRC Climate Platform</title></head>
    <body>
        <h2>{{ report.title }}</h2>
        <p><strong>Type:</strong> {{ report.report_type }}</p>
        <p><strong>Province:</strong> {{ report.province or 'All Provinces' }}</p>
        <p><strong>Status:</strong> {{ report.status }}</p>
        <p><strong>Created:</strong> {{ report.created_at.strftime('%Y-%m-%d %H:%M') }}</p>
        <p><strong>Description:</strong> {{ report.description or 'No description' }}</p>
        
        <h3>Actions</h3>
        <ul>
            <li><a href="{{ url_for('export_report', report_id=report.id, format='pdf') }}">Export as PDF</a></li>
            <li><a href="{{ url_for('export_report', report_id=report.id, format='docx') }}">Export as Word Document</a></li>
        </ul>
        
        <p><a href="{{ url_for('list_reports') }}">Back to Reports</a></p>
    </body>
    </html>
    '''
    return render_template_string(report_page, report=report)

@app.route('/reports/<int:report_id>/export')
@login_required
def export_report(report_id):
    """Export report in specified format."""
    report = Report.query.get_or_404(report_id)
    export_format = request.args.get('format', 'pdf')
    
    # Check if user owns the report or is admin
    if report.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('list_reports'))
    
    # For now, return a simple response
    # In production, this would generate actual PDF/Word documents
    return jsonify({
        'message': f'Export functionality for {export_format} format will be implemented in export_enhanced.py',
        'report': report.to_dict(),
        'format': export_format,
        'includes_logo': True,
        'includes_signature': True
    })

# API endpoints
@app.route('/api/provinces')
def api_provinces():
    """API endpoint to get list of DRC provinces."""
    return jsonify({
        'provinces': satellite_client.list_available_provinces(),
        'mapping': satellite_client.DRC_PROVINCE_ADMIN_MAPPING
    })

@app.route('/api/satellite-data/<province>')
def api_satellite_data(province):
    """API endpoint to get satellite data for a province."""
    try:
        data = satellite_client.get_forest_loss_data(province)
        return jsonify(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Error handlers
@app.errorhandler(413)
@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    return "File is too large", 413

if __name__ == '__main__':
    with app.app_context():
        # Create admin user on startup
        try:
            create_admin_user()
        except Exception as e:
            print(f"Note: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)