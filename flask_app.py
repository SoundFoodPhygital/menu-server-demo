"""Flask application entry point.

This file is kept for backwards compatibility with PythonAnywhere.
The application has been refactored into the 'app' package.

Usage:
    Development: flask run
    Production: from flask_app import app as application
"""
import os
from app import create_app
from app.config import DevelopmentConfig, ProductionConfig

# Select config based on environment
config_class = ProductionConfig if os.getenv("FLASK_ENV") == "production" else DevelopmentConfig

# Create app instance
app = create_app(config_class)

if __name__ == "__main__":
    app.run()
