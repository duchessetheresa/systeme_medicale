from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app import db
from app.models import Authentification
from app.services.face_recognition import FaceRecognitionService
import uuid
from app.config import Config

auth_bp = Blueprint('auth', __name__)
face_service = FaceRecognitionService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        if 'face_image' not in request.files:
            flash('Image faciale requise', 'danger')
            return render_template('auth/login.html')
        face_image = request.files['face_image']
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = face_service.verify_face(face_image)
        if not user_id:
            flash('Authentification faciale échouée', 'danger')
            return render_template('auth/login.html')
        auth = Authentification.query.filter_by(utilisateur_id=user_id).first()
        if not auth or not check_password_hash(auth.biometrie, password):
            flash('Identifiants invalides', 'danger')
            return render_template('auth/login.html')
        session['logged_in'] = True
        session['user_id'] = user_id
        session['user_type'] = auth.type_utilisateur
        access_token = create_access_token(identity={
            'user_id': user_id,
            'user_type': auth.type_utilisateur
        })
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        if 'face_image' not in request.files:
            flash('Image faciale requise', 'danger')
            return render_template('auth/register.html')
        face_image = request.files['face_image']
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'patient')
        if not all([username, password]):
            flash('Nom d\'utilisateur et mot de passe requis', 'danger')
            return render_template('auth/register.html')
        user_id = str(uuid.uuid4())
        if not face_service.register_face(user_id, face_image):
            flash('Échec de l\'enregistrement facial', 'danger')
            return render_template('auth/register.html')
        auth = Authentification(
            id=str(uuid.uuid4()),
            utilisateur_id=user_id,
            type_utilisateur=user_type,
            biometrie=generate_password_hash(password)
        )
        db.session.add(auth)
        db.session.commit()
        flash('Inscription réussie ! Veuillez vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('user_type', None)
    flash('Vous êtes déconnecté', 'success')
    return redirect(url_for('main.home'))

@auth_bp.route('/api/auth', methods=['GET'])
def auth_info():
    return jsonify({
        'message': 'Endpoint d\'authentification',
        'available_routes': {
            'register': {'method': 'POST', 'path': '/api/auth/register'},
            'login': {'method': 'POST', 'path': '/api/auth/login'}
        }
    }), 200

@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    if 'face_image' not in request.files:
        return jsonify({'error': 'Image faciale requise'}), 400
    face_image = request.files['face_image']
    username = request.form.get('username')
    password = request.form.get('password')
    user_type = request.form.get('user_type', 'patient')
    if not all([username, password]):
        return jsonify({'error': 'Nom d\'utilisateur et mot de passe requis'}), 400
    user_id = str(uuid.uuid4())
    if not face_service.register_face(user_id, face_image):
        return jsonify({'error': 'Échec de l\'enregistrement facial'}), 400
    auth = Authentification(
        id=str(uuid.uuid4()),
        utilisateur_id=user_id,
        type_utilisateur=user_type,
        biometrie=generate_password_hash(password)
    )
    db.session.add(auth)
    db.session.commit()
    return jsonify({
        'message': 'Utilisateur enregistré',
        'user_id': user_id
    }), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    if 'face_image' not in request.files:
        return jsonify({'error': 'Image faciale requise'}), 400
    face_image = request.files['face_image']
    username = request.form.get('username')
    password = request.form.get('password')
    user_id = face_service.verify_face(face_image)
    if not user_id:
        return jsonify({'error': 'Authentification faciale échouée'}), 401
    auth = Authentification.query.filter_by(utilisateur_id=user_id).first()
    if not auth or not check_password_hash(auth.biometrie, password):
        return jsonify({'error': 'Identifiants invalides'}), 401
    access_token = create_access_token(identity={
        'user_id': user_id,
        'user_type': auth.type_utilisateur
    })
    return jsonify({
        'access_token': access_token,
        'user_id': user_id,
        'user_type': auth.type_utilisateur
    }), 200