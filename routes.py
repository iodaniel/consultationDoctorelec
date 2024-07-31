from flask import Blueprint, request, jsonify
from models import db, Consultation
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

consultation_bp = Blueprint('consultation', __name__)

@consultation_bp.route('/consultations', methods=['POST'])
@jwt_required()
def create_consultation():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    patient_id = data.get('patient_id')
    status = data.get('status', 'scheduled')
    notes = data.get('notes')
    consultation_type = data.get('consultation_type', 'general')

    if not doctor_id or not patient_id:
        return jsonify({'error': 'Doctor ID and Patient ID are required'}), 400

    new_consultation = Consultation(
        doctor_id=doctor_id,
        patient_id=patient_id,
        status=status,
        notes=notes,
        consultation_type=consultation_type
    )
    db.session.add(new_consultation)
    db.session.commit()

    return jsonify(new_consultation.to_dict()), 201

@consultation_bp.route('/consultations/<string:consultation_id>', methods=['GET'])
@jwt_required()
def get_consultation(consultation_id):
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({'error': 'Consultation not found'}), 404

    return jsonify(consultation.to_dict()), 200

@consultation_bp.route('/consultations/<string:consultation_id>', methods=['PUT'])
@jwt_required()
def update_consultation(consultation_id):
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({'error': 'Consultation not found'}), 404

    data = request.get_json()
    consultation.status = data.get('status', consultation.status)
    consultation.notes = data.get('notes', consultation.notes)
    consultation.consultation_type = data.get('consultation_type', consultation.consultation_type)
    db.session.commit()

    return jsonify(consultation.to_dict()), 200

@consultation_bp.route('/consultations/<string:consultation_id>', methods=['DELETE'])
@jwt_required()
def delete_consultation(consultation_id):
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return jsonify({'error': 'Consultation not found'}), 404

    db.session.delete(consultation)
    db.session.commit()

    return jsonify({'message': 'Consultation deleted successfully'}), 200

# Helper function to convert SQLAlchemy objects to dictionaries
def consultation_to_dict(self):
    return {
        'id': self.id,
        'doctor_id': self.doctor_id,
        'patient_id': self.patient_id,
        'status': self.status,
        'notes': self.notes,
        'consultation_type': self.consultation_type,
        'created_at': self.created_at,
        'updated_at': self.updated_at
    }

Consultation.to_dict = consultation_to_dict
