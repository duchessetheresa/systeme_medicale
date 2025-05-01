from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from app import db
from app.models import Patient, DossierMedical
from flask_jwt_extended import jwt_required
import uuid
from datetime import datetime
from functools import wraps

patients_bp = Blueprint('patients', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@patients_bp.route('/')
@login_required
def list_patients():
    patients = Patient.query.all()
    return render_template('patients/list.html', patients=patients)

@patients_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_patient():
    if request.method == 'POST':
        try:
            patient = Patient(
                id=str(uuid.uuid4()),
                nom=request.form['nom'],
                prenom=request.form['prenom'],
                date_naissance=datetime.strptime(request.form['date_naissance'], '%Y-%m-%d').date(),
                adresse=request.form.get('adresse'),
                donnees_biometriques=request.form.get('donnees_biometriques', '{}')
            )
            
            dossier = DossierMedical(
                id=str(uuid.uuid4()),
                patient_id=patient.id,
                historique_soins='',
                allergies=''
            )
            
            db.session.add(patient)
            db.session.add(dossier)
            db.session.commit()
            
            flash('Patient créé avec succès', 'success')
            return redirect(url_for('patients.list_patients'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {str(e)}', 'danger')
            return render_template('patients/form.html')
    
    return render_template('patients/form.html', is_edit=False)

@patients_bp.route('/<string:patient_id>')
@login_required
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    dossier = DossierMedical.query.filter_by(patient_id=patient_id).first()
    return render_template('patients/detail.html', patient=patient, dossier=dossier)

@patients_bp.route('/<string:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            patient.nom = request.form['nom']
            patient.prenom = request.form['prenom']
            patient.date_naissance = datetime.strptime(request.form['date_naissance'], '%Y-%m-%d').date()
            patient.adresse = request.form.get('adresse')
            patient.donnees_biometriques = request.form.get('donnees_biometriques', '{}')
            
            db.session.commit()
            flash('Patient mis à jour avec succès', 'success')
            return redirect(url_for('patients.list_patients'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {str(e)}', 'danger')
            return render_template('patients/form.html', patient=patient, is_edit=True)
    
    return render_template('patients/form.html', patient=patient, is_edit=True)

@patients_bp.route('/api/patients', methods=['GET'])
@jwt_required()
def get_patients():
    patients = Patient.query.all()
    return jsonify([{
        'id': p.id,
        'nom': p.nom,
        'prenom': p.prenom,
        'date_naissance': p.date_naissance.isoformat() if p.date_naissance else None,
        'adresse': p.adresse
    } for p in patients]), 200

@patients_bp.route('/api/patients', methods=['POST'])
@jwt_required()
def api_create_patient():
    data = request.get_json()
    
    if not all(field in data for field in ['nom', 'prenom', 'date_naissance']):
        return jsonify({'error': 'Données manquantes'}), 400
    
    try:
        patient = Patient(
            id=str(uuid.uuid4()),
            nom=data['nom'],
            prenom=data['prenom'],
            date_naissance=datetime.strptime(data['date_naissance'], '%Y-%m-%d').date(),
            adresse=data.get('adresse'),
            donnees_biometriques=data.get('donnees_biometriques', '{}')
        )
        
        dossier = DossierMedical(
            id=str(uuid.uuid4()),
            patient_id=patient.id,
            historique_soins='',
            allergies=''
        )
        
        db.session.add(patient)
        db.session.add(dossier)
        db.session.commit()
        
        return jsonify({
            'message': 'Patient créé avec succès',
            'id': patient.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@patients_bp.route('/api/patients/<string:patient_id>', methods=['GET'])
@jwt_required()
def get_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    dossier = DossierMedical.query.filter_by(patient_id=patient_id).first()
    
    return jsonify({
        'id': patient.id,
        'nom': patient.nom,
        'prenom': patient.prenom,
        'date_naissance': patient.date_naissance.isoformat() if p.date_naissance else None,
        'adresse': patient.adresse,
        'dossier_medical': {
            'id': dossier.id if dossier else None,
            'allergies': dossier.allergies if dossier else None,
            'historique_soins': dossier.historique_soins if dossier else None
        }
    }), 200
