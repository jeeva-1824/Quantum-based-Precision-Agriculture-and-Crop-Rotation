from datetime import datetime
from flask_login import UserMixin
import enum

from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(256))
    city = db.Column(db.String(64), default="Coimbatore")
    state = db.Column(db.String(64), default="Tamil Nadu")
    is_admin = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    farms = db.relationship('Farm', backref='owner', lazy=True)
    queries = db.relationship('Query', backref='user', lazy=True)
    recommendations = db.relationship('UserRecommendation', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Farm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(256))
    area = db.Column(db.Float)  # in acres
    soil_type = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    crops = db.relationship('CropCycle', backref='farm', lazy=True)
    soil_data = db.relationship('SoilData', backref='farm', lazy=True)
    
    def __repr__(self):
        return f'<Farm {self.name}>'

class SoilData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    moisture_level = db.Column(db.Float)  # in percentage
    ph_value = db.Column(db.Float)
    nitrogen = db.Column(db.Float)  # in ppm
    phosphorus = db.Column(db.Float)  # in ppm
    potassium = db.Column(db.Float)  # in ppm
    temperature = db.Column(db.Float)  # in Celsius
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SoilData {self.id} for Farm {self.farm_id}>'

class CropCycle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    crop_name = db.Column(db.String(128), nullable=False)
    planting_date = db.Column(db.Date)
    harvesting_date = db.Column(db.Date)
    yield_amount = db.Column(db.Float)  # in kg or as appropriate
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CropCycle {self.crop_name} at Farm {self.farm_id}>'

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    land_type = db.Column(db.String(64))
    soil_type = db.Column(db.String(64))
    previous_crop = db.Column(db.String(128))
    previous_yield = db.Column(db.Float)
    recommended_crop = db.Column(db.String(128))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Query {self.id} by User {self.user_id}>'

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(64), default="Coimbatore")
    temperature = db.Column(db.Float)  # in Celsius
    humidity = db.Column(db.Float)  # in percentage
    pressure = db.Column(db.Float)  # in hPa
    wind_speed = db.Column(db.Float)  # in km/h
    conditions = db.Column(db.String(64))  # like "Sunny", "Rainy", etc.
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WeatherData {self.id} for {self.city}>'

class UserRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    crop_name = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserRecommendation {self.id} by User {self.user_id}>'

class ContactMessageStatus(enum.Enum):
    NEW = 'new'
    READ = 'read'
    REPLIED = 'replied'
    ARCHIVED = 'archived'

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(128))
    message = db.Column(db.Text, nullable=False)
    inquiry_type = db.Column(db.String(64))
    status = db.Column(db.Enum(ContactMessageStatus), default=ContactMessageStatus.NEW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional relation to user if logged in
    
    # Admin reply
    admin_reply = db.Column(db.Text)
    replied_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='contact_messages', lazy=True, foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<ContactMessage {self.id} from {self.email}>'

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    search_term = db.Column(db.String(128))
    search_type = db.Column(db.String(64))  # e.g., 'crop', 'soil', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='search_history', lazy=True)
    
    def __repr__(self):
        return f'<SearchHistory {self.id} by User {self.user_id}: {self.search_term}>'
