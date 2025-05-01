from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from datetime import datetime
from app import db
from app.models import DossierMedical, CompteRendu, Traitement
from flask_jwt_extended import jwt_required
import uuid
from functools import wraps

records_bp = Blueprint('records', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login'))
        if session.get('user_type') != 'professionnel':
            flash('Accès réservé aux professionnels', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@records_bp.route('/')
@login_required
def list_records():
    return render_template('records/list.html')

@records_bp.route('/<string:dossier_id>')
@login_required
def dossier_detail(dossier_id):
    dossier = DossierMedical.query.get_or_404(dossier_id)
    comptes_rendus = CompteRendu.query.filter_by(dossier_id=dossier_id).all()
    return render_template('records/dossier.html', dossier=dossier, comptes_rendus=comptes_rendus)

@records_bp.route('/<string:dossier_id>/new', methods=['GET', 'POST'])
@login_required
def create_compte_rendu(dossier_id):
    if request.method == 'POST':
        try:
            compte_rendu = CompteRendu(
                id=str(uuid.uuid4()),
                date=datetime.utcnow(),
                contenu=request.form['contenu'],
                auteur_id=session['user_id'],
                dossier_id=dossier_id
            )
            
            db.session.add(compte_rendu)
            
            for i in range(len(request.form.getlist('traitement_medicament'))):
                if request.form.getlist('traitement_medicament')[i]:
                    traitement = Traitement(
                        id=str(uuid.uuid4()),
                        description=request.form.getlist('traitement_description')[i],
                        medicament=request.form.getlist('traitement_medicament')[i],
                        posologie=request.form.getlist('traitement_posologie')[i],
                        duree=request.form.getlist('traitement_duree')[i],
                        compte_rendu_id=compte_rendu.id
                    )
                    db.session.add(traitement)
            
            db.session.commit()
            flash('Compte rendu créé avec succès', 'success')
            return redirect(url_for('records.dossier_detail', dossier_id=dossier_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {str(e)}', 'danger')
            return render_template('records/record_form.html', dossier_id=dossier_id)
    
    return render_template('records/record_form.html', dossier_id=dossier_id)

@records_bp.route('/api/records/dossier/<string:dossier_id>', methods=['GET'])
@jwt_required()
def get_dossier(dossier_id):
    dossier = DossierMedical.query.get_or_404(dossier_id)
    comptes_rendus = CompteRendu.query.filter_by(dossier_id=dossier_id).all()
    
    return jsonify({
        'id': dossier.id,
        'patient_id': dossier.patient_id,
        'allergies': dossier.allergies,
        'historique_soins': dossier.historique_soins,
        'comptes_rendus': [{
            'id': cr.id,
            'date': cr.date.isoformat(),
            'contenu': cr.contenu,
            'auteur_id': cr.auteur_id,
            'traitements': [{
                'id': t.id,
                'description': t.description,
                'medicament': t.medicament,
                'posologie': t.posologie,
                'duree': t.duree
            } for t in cr.traitements]
        } for cr in comptes_rendus]
    }), 200

@records_bp.route('/api/records/compte-rendu', methods=['POST'])
@jwt_required()
def create_compte_rendu_api():
    data = request.get_json()
    
    required_fields = ['contenu', 'auteur_id', 'dossier_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Données manquantes'}), 400
    
    try:
        compte_rendu = CompteRendu(
            id=str(uuid.uuid4()),
            date=datetime.utcnow(),
            contenu=data['contenu'],
            auteur_id=data['auteur_id'],
            dossier_id=data['dossier_id']
        )
        
        db.session.add(compte_rendu)
        
        for traitement_data in data.get('traitements', []):
            traitement = Traitement(
                id=str(uuid.uuid4()),
                description=traitement_data.get('description'),
                medicament=traitement_data.get('medicament'),
                posologie=traitement_data.get('posologie'),
                duree=traitement_data.get('duree'),
                compte_rendu_id=compte_rendu.id
            )
            db.session.add(traitement)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Compte rendu créé avec succès',
            'id': compte_rendu.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@records_bp.route('/api/records/dossier/<string:dossier_id>/update', methods=['PUT'])
@jwt_required()
def update_dossier(dossier_id):
    dossier = DossierMedical.query.get_or_404(dossier_id)
    data = request.get_json()
    
    if 'allergies' in data:
        dossier.allergies = data['allergies']
    if 'historique_soins' in data:
        dossier.historique_soins = data['historique_soins']
    
    db.session.commit()
    
    return jsonify({'message': 'Dossier médical mis à jour'}), 200 
