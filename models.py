"""
Database models for DRC climate action reporting platform using Flask-SQLAlchemy.
Provides secure user management, file upload tracking, and report management.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Text, JSON
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(200))
    role = db.Column(db.String(50), default='user')  # user, admin, ministry_official
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    uploads = db.relationship('FileUpload', backref='user', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def is_ministry_official(self):
        """Check if user is ministry official."""
        return self.role == 'ministry_official'
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'organization': self.organization,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class FileUpload(db.Model):
    """Model for tracking file uploads."""
    
    __tablename__ = 'file_uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    mime_type = db.Column(db.String(100))
    file_type = db.Column(db.String(50))  # e.g., 'satellite_data', 'emission_data', 'forest_data'
    province = db.Column(db.String(100))  # DRC province
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    file_metadata = db.Column(JSON)  # Store additional file metadata
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        """Convert file upload to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'file_type': self.file_type,
            'province': self.province,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'processed': self.processed,
            'processing_status': self.processing_status,
            'file_metadata': self.file_metadata,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<FileUpload {self.filename}>'

class Report(db.Model):
    """Model for climate action reports."""
    
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(Text)
    report_type = db.Column(db.String(50))  # e.g., 'forest_loss', 'emission_inventory', 'carbon_credit'
    province = db.Column(db.String(100))  # DRC province
    reporting_period_start = db.Column(db.Date)
    reporting_period_end = db.Column(db.Date)
    status = db.Column(db.String(50), default='draft')  # draft, in_review, approved, published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Report data and metadata
    data = db.Column(JSON)  # Store report data as JSON
    charts_config = db.Column(JSON)  # Store chart configurations
    export_settings = db.Column(JSON)  # Store export preferences
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    exports = db.relationship('ReportExport', backref='report', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert report to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'report_type': self.report_type,
            'province': self.province,
            'reporting_period_start': self.reporting_period_start.isoformat() if self.reporting_period_start else None,
            'reporting_period_end': self.reporting_period_end.isoformat() if self.reporting_period_end else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'data': self.data,
            'charts_config': self.charts_config,
            'export_settings': self.export_settings,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<Report {self.title}>'

class ReportExport(db.Model):
    """Model for tracking report exports."""
    
    __tablename__ = 'report_exports'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    export_format = db.Column(db.String(20), nullable=False)  # pdf, docx, xlsx
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    export_date = db.Column(db.DateTime, default=datetime.utcnow)
    includes_charts = db.Column(db.Boolean, default=False)
    includes_logo = db.Column(db.Boolean, default=True)
    includes_signature = db.Column(db.Boolean, default=True)
    export_settings = db.Column(JSON)  # Store export-specific settings
    
    # Foreign keys
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='exports')
    
    def to_dict(self):
        """Convert export to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'export_format': self.export_format,
            'filename': self.filename,
            'file_size': self.file_size,
            'export_date': self.export_date.isoformat() if self.export_date else None,
            'includes_charts': self.includes_charts,
            'includes_logo': self.includes_logo,
            'includes_signature': self.includes_signature,
            'export_settings': self.export_settings,
            'report_id': self.report_id,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<ReportExport {self.filename}>'

# Helper functions for database operations
def init_db(app):
    """Initialize database with app context."""
    db.init_app(app)
    with app.app_context():
        db.create_all()

def create_admin_user(username='admin', email='admin@ministry.cd', password='admin123', 
                     first_name='System', last_name='Administrator'):
    """Create default admin user."""
    admin = User.query.filter_by(username=username).first()
    if not admin:
        admin = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            organization='DRC Ministry of Environment',
            role='admin',
            is_active=True,
            is_verified=True
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully")
    else:
        print(f"Admin user '{username}' already exists")
    return admin

def get_user_by_username(username):
    """Get user by username."""
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    """Get user by email."""
    return User.query.filter_by(email=email).first()

def create_user(username, email, password, first_name, last_name, organization=None, role='user'):
    """Create a new user."""
    # Check if user exists
    if get_user_by_username(username) or get_user_by_email(email):
        raise ValueError("User with this username or email already exists")
    
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        organization=organization,
        role=role
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user