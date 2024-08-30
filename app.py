# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from dotenv import load_dotenv
from routes import consultation_bp
from models import db, Consultation
import os
from flask_mail import Mail, Message   
# Cargar las variables de entorno del archivo .env
load_dotenv()

# Inicializar extensiones
migrate = Migrate()
jwt = JWTManager()

# Crear la aplicación
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configurar CORS
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:3001"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})

    # CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:3001"]}})

    #CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # mail.init_app(app) 
    mail = Mail(app)

    app.register_blueprint(consultation_bp, url_prefix='/api')

    with app.app_context():
        # msg = Message("Test Email", 
        #           sender="support@telehealthconnex.com", 
        #           recipients=["iodanielml@gmail.com"])
        # msg.body = "This is a test email sent from Flask"
        # try:
        #     mail.send(msg)
        #     print("Email sent successfully")
        # except Exception as e:
        #     print(f"Failed to send email: {str(e)}")
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
