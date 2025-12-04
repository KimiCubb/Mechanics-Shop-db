import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
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
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    CACHE_TYPE = "SimpleCache"  # Lightweight in-memory cache for tests
    RATELIMIT_ENABLED = False  # Disable rate limiting during tests

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Database URI should be set via environment variable in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
    
    # Caching with Redis
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')
    
    # Rate limiting with Redis
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'redis://localhost:6379/1')