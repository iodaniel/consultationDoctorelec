from flask import Blueprint, request, jsonify, current_app
from models import db, Consultation
from flask_jwt_extended import jwt_required, get_jwt_identity,  get_jwt
from collections import deque
from threading import Timer
import logging
from flask_mail import Message


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


# @consultation_bp.route('/consultations', methods=['POST'])
# @jwt_required()
# def create_consultation():
#     data = request.get_json()
#     doctor_id = data.get('doctor_id')
#     patient_id = get_jwt_identity()  # Obtener el ID del paciente autenticado
#     jwt_claims = get_jwt()

#     # Obtener la información del doctor desde la base de datos de perfiles
#     doctor_info = get_profile_info(doctor_id)
#     if not doctor_info:
#         return jsonify({'error': 'Doctor profile not found'}), 404

#     # Obtener la información del paciente desde la base de datos de perfiles
#     patient_info = get_profile_info(patient_id)
#     if not patient_info:
#         return jsonify({'error': 'Patient profile not found'}), 404

#     # Debug: Imprimir los IDs y correos electrónicos para verificar
#     current_app.logger.debug(f"Doctor Info: {doctor_info}")
#     current_app.logger.debug(f"Patient Info: {patient_info}")

#     status = data.get('status', 'scheduled')
#     notes = data.get('notes')
#     consultation_type = data.get('consultation_type', 'general')

#     if not doctor_id or not patient_id:
#         return jsonify({'error': 'Doctor ID and Patient ID are required'}), 400

#     new_consultation = Consultation(
#         doctor_id=doctor_id,
#         patient_id=patient_id,
#         status=status,
#         notes=notes,
#         consultation_type=consultation_type
#     )
#     db.session.add(new_consultation)
#     db.session.commit()

#     send_consultation_email(doctor_info, patient_info, new_consultation.id)

#     return jsonify(new_consultation.to_dict()), 201

# def get_profile_info(user_id):
#     """Obtener la información del perfil desde el servicio de perfiles."""
#     try:
#         response = requests.get(f"{PROFILE_SERVICE_URL}/profiles/{user_id}")
#         response.raise_for_status()
#         profile = response.json()
#         return {
#             'email': profile.get('email'),
#             'first_name': profile.get('first_name'),
#             'last_name': profile.get('last_name')
#         }
#     except requests.RequestException as e:
#         current_app.logger.error(f"Failed to fetch profile for user ID {user_id}: {str(e)}")
#         return None

# def send_consultation_email(doctor_info, patient_info, consultation_id):
#     # Crear el mensaje para el doctor
#     mail = current_app.extensions.get('mail')
    
#     if not mail:
#         current_app.logger.error("Failed to send email: Mail extension is not initialized.")
#         return

#     current_app.logger.debug(f"Preparing to send email to Doctor: {doctor_info['email']} and Patient: {patient_info['email']}")
    
#     msg_doctor = Message("Nueva Consulta Programada", recipients=[doctor_info['email']])
#     msg_doctor.body = (
#         f"Hola Dr. {doctor_info['first_name']} {doctor_info['last_name']},\n\n"
#         f"Tienes una nueva consulta programada con el paciente {patient_info['first_name']} {patient_info['last_name']}.\n"
#         f"ID de la consulta: {consultation_id}."
#     )

#     # Crear el mensaje para el paciente
#     msg_patient = Message("Consulta Creada", recipients=[patient_info['email']])
#     msg_patient.body = (
#         f"Hola {patient_info['first_name']} {patient_info['last_name']},\n\n"
#         f"Tu consulta con el Dr. {doctor_info['first_name']} {doctor_info['last_name']} ha sido creada.\n"
#         f"ID de la consulta: {consultation_id}."
#     )

#     # Enviar los correos electrónicos
#     with current_app.app_context():
#         try:
#             current_app.logger.debug("Sending email to doctor...")
#             mail.send(msg_doctor)
#             current_app.logger.debug("Email to doctor sent successfully.")
#             current_app.logger.debug("Sending email to patient...")
#             mail.send(msg_patient)
#             current_app.logger.debug("Email to patient sent successfully.")
#             current_app.logger.debug(f"Emails sent to doctor {doctor_info['email']} and patient {patient_info['email']} for consultation ID: {consultation_id}")
#         except Exception as e:
#             current_app.logger.error(f"Failed to send email: {str(e)}")

            #version solo manda el correo al paciente 
@consultation_bp.route('/consultations', methods=['POST'])
@jwt_required()
def create_consultation():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    patient_id = get_jwt_identity()  # Obtener el ID del paciente autenticado
       # Debug: Imprimir los IDs para verificar
    jwt_claims = get_jwt()

    # Extraer correo electrónico del JWT
    patient_email = jwt_claims.get('email', None)
    patient_firstName = jwt_claims.get('first_name', None)
    patient_lastName = jwt_claims.get('last_name', None)
    patient_username = jwt_claims.get('username', None)
    doctor_email = data.get('email', None)
    doctor_firstName = data.get('first_name', None)
    doctor_lastName = data.get('doctor.last_name', None)

    
    # Debug: Imprimir los IDs para verificar
    # current_app.logger.debug(f"Patient Name : { patient_firstName} {patient_lastName}")
    # current_app.logger.debug(f"Doctor Name : { doctor_firstName} {doctor_lastName}")
    current_app.logger.debug(f"Doctor ID from request: {doctor_id}")
    current_app.logger.debug(f"Patient ID from JWT: {patient_id}")
    current_app.logger.debug(f"Patient Email from JWT: {patient_email}")
    current_app.logger.debug(f"Doctor Email from data get: {doctor_email}")
    

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
        'email': doctor_email,
        'first_name': doctor_firstName,
        'last_name': doctor_lastName
        
    }
        
    patient_info = {
            'email': patient_email,
            'first_name': patient_firstName,
            'last_name': patient_firstName
           
    }

    send_consultation_email(doctor_info, patient_info, new_consultation.id)

    return jsonify(new_consultation.to_dict()), 201
    

def send_consultation_email(doctor_info, patient_info, consultation_id):
    # Crear el mensaje para el doctor
    mail = current_app.extensions.get('mail')
    
    if not mail:
        current_app.logger.error("Failed to send email: Mail extension is not initialized.")
        return

    current_app.logger.debug(f"Preparing to send email to Doctor: {doctor_info['email']} and Patient: {patient_info['email']}")
    
    msg_doctor = Message("Nueva Consulta Programada", recipients=[doctor_info['email']])
    msg_doctor.body = (
        f"Hola Dr. {doctor_info['first_name']} {doctor_info['last_name']},\n\n"
        f"Tienes una nueva consulta programada con el paciente {patient_info['first_name']} {patient_info['last_name']}.\n"
        f"ID de la consulta: {consultation_id}."
    )

    # Crear el mensaje para el paciente
    msg_patient = Message("Consulta Creada", recipients=[patient_info['email']])
    msg_patient.body = (
        f"Hola {patient_info['first_name']} {patient_info['last_name']},\n\n"
        f"Tu consulta con el Dr. {doctor_info['first_name']} {doctor_info['last_name']} ha sido creada.\n"
        f"ID de la consulta: {consultation_id}."
    )

    # Enviar los correos electrónicos
    with current_app.app_context():
        try:
            current_app.logger.debug("Sending email to doctor...")
            mail.send(msg_doctor)
            current_app.logger.debug("Email to doctor sent successfully.")
            current_app.logger.debug("Sending email to patient...")
            mail.send(msg_patient)
            current_app.logger.debug("Email to patient sent successfully.")
            current_app.logger.debug(f"Emails sent to doctor {doctor_info['email']} and patient {patient_info['email']} for consultation ID: {consultation_id}")
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")

# def send_consultation_email(doctor_info, patient_info, consultation_id):
#     # Crear el mensaje para el doctor
#     mail = current_app.extensions.get('mail')
    
#     if not mail:
#         current_app.logger.error("Failed to send email: Mail extension is not initialized.")
#         return

#     current_app.logger.debug(f"Preparing to send email to Doctor: {doctor_info['email']} and Patient: {patient_info['email']}")
    
#     msg_doctor = Message("Nueva Consulta Programada", recipients=[doctor_info['email']])
#     msg_doctor.body = (
#         f"Hola Dr. {doctor_info['user_name']},\n\n"
#         f"Tienes una nueva consulta programada con el paciente {patient_info['user_name']}.\n"
#         f"ID de la consulta: {consultation_id}."
#     )

#     # Crear el mensaje para el paciente
#     msg_patient = Message("Consulta Creada", recipients=[patient_info['email']])
#     msg_patient.body = (
#         f"Hola {patient_info['user_name']},\n\n"
#         f"Tu consulta con el Dr. {doctor_info['user_name']} ha sido creada.\n"
#         f"ID de la consulta: {consultation_id}."
#     )

#     # Enviar los correos electrónicos
#     with current_app.app_context():
#         try:
#             current_app.logger.debug("Sending email to doctor...")
#             mail.send(msg_doctor)
#             current_app.logger.debug("Email to doctor sent successfully.")
#             current_app.logger.debug("Sending email to patient...")
#             mail.send(msg_patient)
#             current_app.logger.debug("Email to patient sent successfully.")
#             current_app.logger.debug(f"Emails sent to doctor {doctor_info['email']} and patient {patient_info['email']} for consultation ID: {consultation_id}")
#         except Exception as e:
#             current_app.logger.error(f"Failed to send email: {str(e)}")


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
