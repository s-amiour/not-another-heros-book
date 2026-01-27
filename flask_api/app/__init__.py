from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db
from .routes import main_bp

# This file replaces the top of our old app.py. It initializes the app and "registers" the other pieces.
# Initialize app + Configs

def create_app(config_class=Config):
    # Create WSGI app instance
    app = Flask(__name__)

    # Config purposes
    app.config.from_object(config_class)

    # Bind app to DB obj, maintaining Application Factory pattern
    db.init_app(app)

    # Allow communication between frontend and backend
    CORS(app)

    # Register Routes
    app.register_blueprint(main_bp)

    # Create DB (Level 10 only)
    with app.app_context():
        db.create_all()

    return app