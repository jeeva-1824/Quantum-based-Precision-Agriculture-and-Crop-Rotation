import os
import logging

from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
# Ensure Flask-WTF is installed: pip install flask-wtf
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from extensions import db, csrf, login_manager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "quantum_agriculture_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database, using SQLite as a fallback
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    logging.warning("DATABASE_URL not set. Falling back to SQLite.")
    database_url = "sqlite:///quantum_agriculture.db"
app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# Log the database URL for debugging
logging.info(f"Using database URL: {database_url}")

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions with the app
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page'
login_manager.login_message_category = 'info'

# Custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to <br> tags for display in HTML"""
    if text:
        return text.replace('\n', '<br>')
    return ""

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon.ico file"""
    static_folder = os.path.join(app.root_path, 'static')
    if os.path.exists(os.path.join(static_folder, 'favicon.ico')):
        return send_from_directory(static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    logging.warning("favicon.ico not found in static directory")
    return "", 404

@app.route('/test-admin')
def test_admin():
    """Test admin login and database connection"""
    try:
        # Check if the admin user exists
        admin_email = 'farmhub04@gmail.com'
        admin = models.User.query.filter_by(email=admin_email).first()
        
        if admin and admin.is_admin:
            return f"Admin user '{admin.username}' with email '{admin_email}' exists and is an admin.", 200
        else:
            return "Admin user not found or not set as admin.", 404
    except Exception as e:
        logging.error(f"Error testing admin login: {e}")
        return f"Error: {e}", 500

@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.query.get(int(user_id))
    except Exception as e:
        logging.error(f"Error loading user: {e}")
        return None

with app.app_context():
    # Import models after initializing db to avoid circular imports
    import models
    try:
        # Create all tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_email = 'farmhub04@gmail.com'
        
        # First check by email
        admin = models.User.query.filter_by(email=admin_email).first()
        
        # If not found by email, check for existing admin user
        admin_user = models.User.query.filter_by(username='admin').first()
        
        if admin:
            # Email exists, make sure it's an admin
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
                logging.info(f'User {admin_email} set as admin')
        elif admin_user:
            # Username 'admin' exists but with a different email
            admin_user.email = admin_email
            admin_user.is_admin = True
            db.session.commit()
            logging.info(f'Admin user updated with email {admin_email}')
        else:
            # Create new admin user
            admin = models.User(
                username='farmhub_admin',
                email=admin_email,
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                first_name='Admin',
                last_name='User',
                city='Coimbatore',
                state='Tamil Nadu'
            )
            db.session.add(admin)
            db.session.commit()
            logging.info('Admin user created successfully')
    except Exception as e:
        logging.error(f"Error during database initialization: {e}")
