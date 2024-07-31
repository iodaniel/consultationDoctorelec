from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from dotenv import load_dotenv
import os

# Cargar las variables de entorno del archivo .env
load_dotenv()

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# Crear la aplicación
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configurar CORS
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    # Configuración de Stripe
    # stripe.api_key = app.config['STRIPE_PRIVATE_KEY']

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Registrar el blueprint de facturación con el prefijo /api
    from routes import consultation_bp 
    app.register_blueprint(consultation_bp , url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)