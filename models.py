from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Consultation(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = db.Column(db.Integer, nullable=False)
    patient_id = db.Column(db.Integer, nullable=False)
    #scheduled_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    status = db.Column(db.String(20), nullable=False, default="scheduled")
    notes = db.Column(db.Text, nullable=True)
    consultation_type = db.Column(db.String(50), nullable=False, default="general")
    #prescription = db.Column(db.Text, nullable=True)
    #cost = db.Column(db.Float, nullable=False, default=0.0)
    #results = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
