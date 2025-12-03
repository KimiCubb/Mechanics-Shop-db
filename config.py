import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    
    # Rate Limiting
    RATELIMIT_STORAGE_URI = "memory://"
    
    # Caching
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default

class DevelopmentConfig(Config):
    """Development configuration"""
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        'mysql+mysqlconnector://root:rootuser1@localhost/mechanic_shop_db')
    DEBUG = True
    SQLALCHEMY_ECHO = True
    CACHE_DEFAULT_TIMEOUT = 60  # Shorter cache for development
    RATELIMIT_ENABLED = True  # Set to False to disable rate limiting for testing

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CACHE_TYPE = "NullCache"  # Disable caching during tests
    RATELIMIT_ENABLED = False  # Disable rate limiting during tests

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    CACHE_TYPE = "RedisCache"  # Use Redis in production
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    RATELIMIT_STORAGE_URI = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')