from flask import Blueprint, jsonify
from app.services.gita_service import GitaService
from app import cache
import os

bp = Blueprint('shloks', __name__)
gita_service = GitaService(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'gita-shloks.json'))

@bp.route('/shloks/<int:chapter>/<int:verse>')
@cache.cached(timeout=3600)
def get_shlok(chapter, verse):
    shlok = gita_service.get_shlok(chapter, verse)
    if not shlok:
        return jsonify({'error': 'Shlok not found'}), 404
    return jsonify(shlok) 