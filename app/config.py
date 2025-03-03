import os

class Config:
    DEBUG = True
    TESTING = False
    CACHE_TYPE = 'simple'  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 300
    API_KEY = os.environ.get('API_KEY', 'your_default_api_key')
