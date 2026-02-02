"""
Configuration settings for Flask Blog API.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration."""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = timedelta(hours=24)  # Token expires in 24 hours
    
    # API Settings
    API_TITLE = 'Flask Blog API'
    API_VERSION = '1.0.0'
    API_DESCRIPTION = 'Blog API with RBAC authorization'
    
    # CORS Settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000']
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Domain (for multi-tenancy)
    DEFAULT_DOMAIN = 'default'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    def __init__(self):
        """Validate production config on instantiation."""
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production")
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in production")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    JWT_EXPIRATION = timedelta(minutes=5)  # Shorter for tests


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment."""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
