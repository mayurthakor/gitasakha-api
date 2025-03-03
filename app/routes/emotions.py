from flask import Blueprint, jsonify
from app.services.gita_service import GitaService
from app import cache
from app.schemas import (
    EmotionsResponseSchema, 
    EmotionDetailSchema, 
    ThemeShloksResponseSchema,
    ErrorResponseSchema
)
from flask_apispec import marshal_with, doc
from marshmallow import fields
import os

bp = Blueprint('emotions', __name__)
gita_service = GitaService(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'gita-shloks.json'))

@bp.route('/emotions')
@doc(tags=['Emotions'],
     description='Get list of all emotions with their basic details')
@marshal_with(EmotionsResponseSchema)
@cache.cached(timeout=3600)
def get_emotions():
    emotions_data = gita_service.get_emotions()
    formatted_emotions = []
    for name, data in emotions_data.items():
        formatted_emotions.append({
            "name": name,
            "emoji": data["emoji"],
            "color": data["color"],
            "themes": list(data["themes"].keys())
        })
    return {'emotions': formatted_emotions}

@bp.route('/emotions/<string:emotion>')
@doc(tags=['Emotions'],
     description='Get detailed information about a specific emotion',
     parameters=[{
         'in': 'path',
         'name': 'emotion',
         'required': True,
         'description': 'Name of the emotion',
         'schema': {'type': 'string'}
     }])
@marshal_with(EmotionDetailSchema, code=200)
@marshal_with(ErrorResponseSchema, code=404)
@cache.cached(timeout=3600)
def get_emotion_detail(emotion):
    emotion_detail = gita_service.get_emotion_detail(emotion)
    if not emotion_detail:
        return {'error': 'Emotion not found'}, 404
    
    formatted_themes = []
    for theme_name, theme_data in emotion_detail["themes"].items():
        formatted_themes.append({
            "name": theme_name,
            "description": theme_data["description"]
        })
    
    return {
        "name": emotion,
        "emoji": emotion_detail["emoji"],
        "color": emotion_detail["color"],
        "themes": formatted_themes
    }

@bp.route('/emotions/<string:emotion>/themes/<string:theme>')
@doc(tags=['Emotions'],
     description='Get all shloks for a specific theme under an emotion',
     parameters=[{
         'in': 'path',
         'name': 'emotion',
         'required': True,
         'description': 'Name of the emotion',
         'schema': {'type': 'string'}
     },
     {
         'in': 'path',
         'name': 'theme',
         'required': True,
         'description': 'Name of the theme',
         'schema': {'type': 'string'}
     }])
@marshal_with(ThemeShloksResponseSchema, code=200)
@marshal_with(ErrorResponseSchema, code=404)
@cache.cached(timeout=3600)
def get_theme_shloks(emotion, theme):
    shloks = gita_service.get_theme_shloks(emotion, theme)
    if not shloks:
        return {'error': 'Theme or emotion not found'}, 404
    return {'shloks': shloks} 