from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from flask_apispec import FlaskApiSpec
from flask_apispec.extension import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from app.config import Config

cache = Cache()
docs = FlaskApiSpec()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Swagger configuration
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='GitaSakha API',
            version='v1',
            plugins=[MarshmallowPlugin()],
            openapi_version='2.0',
            info=dict(
                description='API for serving Bhagavad Gita verses based on emotions and themes',
                contact={"email": "your-email@example.com"}
            ),
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'
    })

    # Initialize extensions
    CORS(app)
    cache.init_app(app)
    docs.init_app(app)

    # Register blueprints
    from app.routes import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix='/v1')

    # Register routes with APISpec
    docs.register_existing_resources()

    @app.route('/')

    @app.route('/')
    def index():
        return {
            'status': 'ok',
            'message': 'Welcome to GitaSakha API',
            'docs_url': '/swagger-ui/'
        }

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}

    return app
