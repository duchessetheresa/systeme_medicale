from flask import Blueprint, render_template, session, redirect, url_for
from app.models import Patient, ProfessionnelSante, DossierMedical
from functools import wraps

main_bp = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'patients': Patient.query.count(),
        'professionals': ProfessionnelSante.query.count(),
        'records': DossierMedical.query.count()
    }
    return render_template('dashboard.html', stats=stats)

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')
