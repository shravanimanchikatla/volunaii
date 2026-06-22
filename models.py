from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='volunteer') # 'volunteer' or 'organizer'
    location = db.Column(db.String(100), nullable=True) # Zip code or city
    skills = db.Column(db.String(255), nullable=True) # Comma separated list of skills
    is_available = db.Column(db.Boolean, default=False)
    
    # BloodLink Profile
    blood_group = db.Column(db.String(5), nullable=True) # For compatibility checking
    blood_type = db.Column(db.String(5), nullable=True) # For template display
    is_emergency_donor = db.Column(db.Boolean, default=False)
    last_donation_date = db.Column(db.DateTime, nullable=True)
    emergency_alerts_enabled = db.Column(db.Boolean, default=True)
    city = db.Column(db.String(100), nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)

    # Relationship to tasks they've accepted
    tasks = db.relationship('Task', backref='volunteer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Cascade delete reports when an organizer is deleted
    organizer = db.relationship('User', backref=db.backref('reports', lazy=True, cascade="all, delete-orphan"))
    # Cascade delete tasks when a report is deleted
    tasks = db.relationship('Task', backref='report', lazy=True, cascade="all, delete-orphan")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    urgency_score = db.Column(db.Integer, nullable=False) # 1-10
    status = db.Column(db.String(20), default='open') # 'open', 'assigned', 'completed'
    assigned_volunteer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    blood_type_needed = db.Column(db.String(5), nullable=False) # Matches template
    units_needed = db.Column(db.Integer, default=1) # Matches template
    hospital_name = db.Column(db.String(200), nullable=False)
    hospital_address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    urgency_score = db.Column(db.Integer, default=5) # Matches template
    status = db.Column(db.String(20), default='Pending') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    assigned_donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    ngo = db.relationship('User', foreign_keys=[ngo_id], backref=db.backref('ngo_blood_requests', lazy=True, cascade="all, delete-orphan"))
    assigned_donor = db.relationship('User', foreign_keys=[assigned_donor_id], backref=db.backref('accepted_blood_donations', lazy=True))

class MissingPersonCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Section 1: Child Info
    name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100))
    dob = db.Column(db.Date, nullable=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    distinctive_features = db.Column(db.Text)
    clothing_last_seen = db.Column(db.Text)
    
    # Section 2: Disappearance
    location_last_seen = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    last_seen_time = db.Column(db.DateTime, default=datetime.utcnow)
    was_child_alone = db.Column(db.String(20))
    cctv_available = db.Column(db.Boolean, default=False)
    witness_info = db.Column(db.Text)
    
    # Section 3: Parent/Guardian
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    parent_relationship = db.Column(db.String(50))
    parent_location = db.Column(db.String(200))
    
    # Section 4: Police & Legal
    fir_number = db.Column(db.String(100))
    police_station = db.Column(db.String(100))
    investigating_officer = db.Column(db.String(100))
    officer_contact = db.Column(db.String(50))
    is_fir_verified = db.Column(db.Boolean, default=False)
    
    # Section 5: Media
    photo_url = db.Column(db.String(500))
    body_photo_url = db.Column(db.String(500))
    family_photo_url = db.Column(db.String(500))
    
    # Section 6: Special Considerations
    medical_conditions = db.Column(db.Text)
    special_needs = db.Column(db.Text)
    description = db.Column(db.Text) # General mission briefing
    
    # Status & Urgency
    urgency_score = db.Column(db.Integer, default=50) # 0-100
    status = db.Column(db.String(20), default='Active') # 'Draft', 'Active', 'Resolved', 'Closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    sighting_records = db.relationship('Sighting', backref='case', lazy=True, cascade="all, delete-orphan")
    organizer = db.relationship('User', foreign_keys=[organizer_id], backref=db.backref('organized_missing_cases', lazy=True, cascade="all, delete-orphan"))

class Sighting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('missing_person_case.id'), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    location_name = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    description = db.Column(db.Text, nullable=False)
    photo_url = db.Column(db.String(500))
    child_condition = db.Column(db.String(100))
    adult_description = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)

    reporter = db.relationship('User', foreign_keys=[reporter_id], backref=db.backref('reported_sightings', lazy=True))

class SearchAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('missing_person_case.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='Assigned') # 'Assigned', 'Accepted', 'Completed', 'Declined'
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    case_rel = db.relationship('MissingPersonCase', backref=db.backref('assignments', lazy=True, cascade="all, delete-orphan"))
    volunteer_rel = db.relationship('User', foreign_keys=[volunteer_id], backref=db.backref('search_missions', lazy=True, cascade="all, delete-orphan"))
