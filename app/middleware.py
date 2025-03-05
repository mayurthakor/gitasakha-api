from flask import request, jsonify
from functools import wraps
import os

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_api_key = os.environ.get('API_KEY')
        print(f"Expected API Key: {expected_api_key}")

        if not api_key or api_key != expected_api_key:
            return jsonify({'message': 'Unauthorized'}), 401

        return f(*args, **kwargs)
    return decorated_function


from collections import defaultdict
from time import time

class RateLimiter:
    def __init__(self, limit=100, per=60):
        self.limit = limit
        self.per = per
        self.calls = defaultdict(list)

    def is_allowed(self, client_id):
        now = time()
        client_calls = self.calls[client_id]
        
        # Remove calls older than the rate limit window
        client_calls = [call for call in client_calls if call > now - self.per]
        self.calls[client_id] = client_calls
        
        if len(client_calls) < self.limit:
            client_calls.append(now)
            return True
        return False

rate_limiter = RateLimiter()

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_id = request.remote_addr  # Use IP address as client identifier
        if not rate_limiter.is_allowed(client_id):
            return jsonify({'message': 'Too Many Requests'}), 429
        return f(*args, **kwargs)
    return decorated_function
