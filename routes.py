from flask import Blueprint, request, jsonify, current_app
from models import db, Consultation
from flask_jwt_extended import jwt_required, get_jwt_identity
from collections import deque
from threading import Timer
import logging
from flask_mail import Message
from app import mail

# Configuración de URLs para otros microservicios
PROFILE_SERVICE_URL = "http://127.0.0.1:5003/api"
PATIENT_SERVICE_URL = "http://127.0.0.1:5004/api"

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

consultation_bp = Blueprint('consultation', __name__)

# Cola FIFO para manejar las consultas
consultation_queue = deque()

# Tiempo de espera para confirmación (en segundos)
CONFIRMATION_TIMEOUT = 180




@consultation_bp.route('/consultations', methods=['POST'])
@jwt_required()
def create_consultation():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    patient_id = get_jwt_identity()  # Obtener el ID del paciente autenticado
       # Debug: Imprimir los IDs para verificar
    current_app.logger.debug(f"Doctor ID from request: {doctor_id}")
    current_app.logger.debug(f"Patient ID from JWT: {patient_id}")

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

    doctor_info = {
        'email': data.get('doctor_email'),
        'first_name': data.get('doctor_first_name'),
        'last_name': data.get('doctor_last_name')
    }
        
    patient_info = {
            'email': data.get('patient_email'),
            'first_name': data.get('patient_first_name'),
            'last_name': data.get('patient_last_name')
    }

    send_consultation_email(doctor_info, patient_info, new_consultation.id)

    return jsonify(new_consultation.to_dict()), 201
    


def send_consultation_email(doctor_info, patient_info, consultation_id):
    # Crear el mensaje para el doctor
    msg_doctor = Message("Nueva Consulta Programada", recipients=[doctor_info['email']])
    msg_doctor.body = (
        f"Hola Dr. {doctor_info['first_name']} {doctor_info['last_name']},\n\n"
        f"Tienes una nueva consulta programada con el paciente {patient_info['first_name']} {patient_info['last_name']}.\n"
        f"ID de la consulta: {consultation_id}."
    )

    # Crear el mensaje para el paciente
    msg_patient = Message("Consulta Creada", recipients=[patient_info['email']])
    msg_patient.body = (
        f"Hola {patient_info['first_name']},\n\n"
        f"Tu consulta con el Dr. {doctor_info['first_name']} {doctor_info['last_name']} ha sido creada.\n"
        f"ID de la consulta: {consultation_id}."
    )

    # Enviar los correos electrónicos
    with current_app.app_context():
        try:
            mail.send(msg_doctor)
            mail.send(msg_patient)
            current_app.logger.debug(f"Emails sent to doctor {doctor_info['email']} and patient {patient_info['email']} for consultation ID: {consultation_id}")
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")


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

@consultation_bp.route('/logs', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_logs():
    if request.method == 'OPTIONS':
        return '', 204

    # Obtener el ID del usuario autenticado
    patient_id = get_jwt_identity()
    # current_app.logger.debug(f"Fetching logs for patient ID: {patient_id}")
    # Consultar las consultas del paciente
    consultations = Consultation.query.filter_by(patient_id=patient_id).all()

    # Convertir las consultas a un formato JSON
    consultations_data = [consultation.to_dict() for consultation in consultations]
    # current_app.logger.debug(f"Consultations for patient {patient_id}: {consultations_data}")
    for consultation in consultations_data:
        current_app.logger.debug(f"Consultation ID: {consultation['id']} - Doctor ID: {consultation.get('doctor_id')} - Patient ID: {consultation.get('patient_id')}")

    
    return jsonify(consultations_data), 200



@consultation_bp.route('/logs-doctor', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_logs_doctor():
    if request.method == 'OPTIONS':
        return '', 204

    # Obtener el ID del doctor autenticado
    doctor_id = get_jwt_identity()
    current_app.logger.debug(f"Fetching logs for doctor ID: {doctor_id}")
    # Consultar las consultas del doctor
    consultations = Consultation.query.filter_by(doctor_id=doctor_id).all()
    #Convertir las consultas a un formato JSON
    consultations_data = [consultation.to_dict() for consultation in consultations]
    current_app.logger.debug(f"Consultations for doctor {doctor_id}: {consultations_data}")


    for consultation in consultations_data:
        current_app.logger.debug(f"Consultation ID: {consultation['id']} - Patient ID: {consultation.get('patient_id')}")


    
    return jsonify(consultations_data), 200
