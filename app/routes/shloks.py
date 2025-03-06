from flask import Blueprint, jsonify, request
from app.services.gita_service import GitaService
from app.middleware import rate_limit
from app import cache
import os
import random

bp = Blueprint('shloks', __name__)
gita_service = GitaService(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'gita-shloks.json'))

@bp.route('/shloks/<int:chapter>/<int:verse>')
@rate_limit
@cache.cached(timeout=3600)
def get_shlok(chapter, verse):
    shlok = gita_service.get_shlok(chapter, verse)
    if not shlok:
        return jsonify({'error': 'Shlok not found'}), 404
    return jsonify(shlok)

@bp.route('/shloks/random/<string:emotion>/<string:theme>')
@rate_limit
@cache.cached(timeout=3600)
def get_random_shlok(emotion, theme):
    shloks = gita_service.get_theme_shloks(emotion, theme)
    if not shloks:
        return jsonify({'error': 'Theme or emotion not found'}), 404
    
    if not shloks['shloks']:
        return jsonify({'error': 'No shloks found for this theme and emotion'}), 404

    random_shlok = random.choice(shloks['shloks'])
    response = jsonify(random_shlok)
    response.headers['Content-Type'] = 'application/json'
    return response
