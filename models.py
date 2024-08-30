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

        
class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.String(36), db.ForeignKey('consultation.id'), nullable=False)
    patient_username = db.Column(db.String(100), nullable=False)
    doctor_username = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    testimonial = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'consultation_id': self.consultation_id,
            'patient_username': self.patient_username,
            'doctor_username': self.doctor_username,
            'rating': self.rating,
            'testimonial': self.testimonial,
            'created_at': self.created_at.isoformat(),
        }

