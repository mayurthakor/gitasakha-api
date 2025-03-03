import json
from typing import List, Dict, Optional
import os

class GitaService:
    def __init__(self, data_path=None):
        self.data_path = data_path or os.path.join('data', 'gita-shloks.json')
        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find gita-shloks.json at {self.data_path}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in gita-shloks.json")

    def get_emotions(self) -> Dict:
        return self.data.get('emotions', {})

    def get_emotion_detail(self, emotion: str) -> Optional[Dict]:
        emotions = self.data.get('emotions', {})
        return emotions.get(emotion)

    def get_theme_shloks(self, emotion: str, theme: str) -> List[Dict]:
        emotions = self.data.get('emotions', {})
        emotion_data = emotions.get(emotion, {})
        themes = emotion_data.get('themes', {})
        theme_data = themes.get(theme, {})
        return theme_data.get('shloks', [])

    def get_shlok(self, chapter: int, verse: int) -> Optional[Dict]:
        shloks = self.data.get('shloks', [])
        return next((s for s in shloks 
                    if s['chapter'] == chapter and s['verse'] == verse), None)

    def search_shloks(self, query: str) -> List[Dict]:
        results = []
        query = query.lower()
        
        # Search through all emotions and themes
        for emotion_data in self.data.get('emotions', {}).values():
            for theme_data in emotion_data.get('themes', {}).values():
                for shlok in theme_data.get('shloks', []):
                    if (query in shlok['sanskrit'].lower() or
                        query in shlok['translation']['english'].lower() or
                        query in shlok['translation']['hindi'].lower()):
                        results.append(shlok)
        
        return results 