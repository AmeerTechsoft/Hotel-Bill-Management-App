import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'  # Replace with your SMTP server
    MAIL_PORT = 587  # Typically 587 for TLS, 465 for SSL
    MAIL_USERNAME = '#'  # Replace with your email address
    MAIL_PASSWORD = '#'  # Replace with your email password
    MAIL_USE_TLS = True  # Use TLS
    MAIL_USE_SSL = False  # Do not use SSL
    MAIL_DEFAULT_SENDER = '#'  # Default sender
