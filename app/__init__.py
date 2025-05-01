from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_session import Session
from app.config import Config
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
sess = Session()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    sess.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Ajouter un filtre personnalisé pour Jinja2
    def datetimeformat(value, format='%Y'):
        if value == 'now':
            value = datetime.now()
        return value.strftime(format)
    
    app.jinja_env.filters['datetimeformat'] = datetimeformat
    
    # Importation et enregistrement des blueprints
    from app.routes.auth import auth_bp
    from app.routes.patients import patients_bp
    from app.routes.professionals import professionals_bp
    from app.routes.records import records_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(patients_bp, url_prefix='/api/patients')
    app.register_blueprint(professionals_bp, url_prefix='/api/professionals')
    app.register_blueprint(records_bp, url_prefix='/api/records')
    app.register_blueprint(main_bp)
    
    # Gestion des erreurs
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint non trouvé'}), 404
    
    return app