from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Consultation(db.Model):
    __tablename__ = 'consultation'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = db.Column(db.Integer, nullable=False)
    patient_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="scheduled")
    notes = db.Column(db.Text, nullable=True)
    consultation_type = db.Column(db.String(50), nullable=False, default="general")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'patient_id': self.patient_id,  # Asegúrate de que esto esté presente
            'status': self.status,
            'notes': self.notes,
            'consultation_type': self.consultation_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }