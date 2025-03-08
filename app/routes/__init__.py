# app/routes/__init__.py
from app.routes.emotions import bp as emotions_bp
from app.routes.shloks import bp as shloks_bp
from app.routes.search import bp as search_bp

blueprints = [emotions_bp, shloks_bp, search_bp]  # Add it to the list
