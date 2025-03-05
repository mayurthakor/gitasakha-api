from flask import Blueprint, jsonify, request
from app.services.gita_service import GitaService
from app.middleware import require_api_key, rate_limit
import os

bp = Blueprint('search', __name__)
gita_service = GitaService(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'gita-shloks.json'))

@bp.route('/search')
@require_api_key
@rate_limit
def search_shloks():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    results = gita_service.search_shloks(query)
    return jsonify({'results': results})
