from marshmallow import Schema, fields

class TranslationSchema(Schema):
    english = fields.Str(required=True, description="English translation")
    hindi = fields.Str(required=True, description="Hindi translation")
    gujarati = fields.Str(description="Gujarati translation")
    marathi = fields.Str(description="Marathi translation")
    tamil = fields.Str(description="Tamil translation")

class ShlokSchema(Schema):
    chapter = fields.Int(required=True, description="Chapter number")
    verse = fields.Int(required=True, description="Verse number")
    sanskrit = fields.Str(required=True, description="Sanskrit verse")
    translation = fields.Nested(TranslationSchema, required=True)
    explanation_url = fields.Str(required=True, description="URL for detailed explanation")

class ThemeSchema(Schema):
    name = fields.Str(required=True, description="Theme name")
    description = fields.Str(required=True, description="Theme description")

class EmotionListSchema(Schema):
    name = fields.Str(required=True, description="Emotion name")
    emoji = fields.Str(required=True, description="Emotion emoji")
    color = fields.Str(required=True, description="Emotion color code")
    themes = fields.List(fields.Str(), required=True, description="List of theme names")

class EmotionDetailSchema(Schema):
    name = fields.Str(required=True, description="Emotion name")
    emoji = fields.Str(required=True, description="Emotion emoji")
    color = fields.Str(required=True, description="Emotion color code")
    themes = fields.List(fields.Nested(ThemeSchema), required=True, description="List of themes")

class EmotionsResponseSchema(Schema):
    emotions = fields.List(fields.Nested(EmotionListSchema), required=True)

class ThemeShloksResponseSchema(Schema):
    shloks = fields.List(fields.Nested(ShlokSchema), required=True)

class SearchResponseSchema(Schema):
    results = fields.List(fields.Nested(ShlokSchema), required=True)

class ErrorResponseSchema(Schema):
    error = fields.Str(required=True) 