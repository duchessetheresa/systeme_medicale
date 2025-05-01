from datetime import datetime
from app import db
from sqlalchemy.dialects.mysql import LONGTEXT

class Etablissement(db.Model):
    __tablename__ = 'Etablissement'
    id = db.Column(db.String(36), primary_key=True)
    nom = db.Column(db.String(100))
    adresse = db.Column(db.String(255))
    type = db.Column(db.String(50))
    professionnels = db.relationship('ProfessionnelSante', backref='etablissement', lazy=True)

class ProfessionnelSante(db.Model):
    __tablename__ = 'ProfessionnelSante'
    id = db.Column(db.String(36), primary_key=True)
    nom = db.Column(db.String(100))
    specialite = db.Column(db.String(100))
    etablissement_id = db.Column(db.String(36), db.ForeignKey('Etablissement.id'))
    comptes_rendus = db.relationship('CompteRendu', backref='auteur', lazy=True)

class Patient(db.Model):
    __tablename__ = 'Patient'
    id = db.Column(db.String(36), primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    date_naissance = db.Column(db.Date)
    adresse = db.Column(db.String(255))
    donnees_biometriques = db.Column(LONGTEXT)
    dossier = db.relationship('DossierMedical', uselist=False, backref='patient')

class Authentification(db.Model):
    __tablename__ = 'Authentification'
    id = db.Column(db.String(36), primary_key=True)
    utilisateur_id = db.Column(db.String(36))
    type_utilisateur = db.Column(db.Enum('patient', 'professionnel'))
    biometrie = db.Column(LONGTEXT)

class DossierMedical(db.Model):
    __tablename__ = 'DossierMedical'
    id = db.Column(db.String(36), primary_key=True)
    patient_id = db.Column(db.String(36), db.ForeignKey('Patient.id'))
    historique_soins = db.Column(LONGTEXT)
    allergies = db.Column(LONGTEXT)
    comptes_rendus = db.relationship('CompteRendu', backref='dossier', lazy=True)

class CompteRendu(db.Model):
    __tablename__ = 'CompteRendu'
    id = db.Column(db.String(36), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    contenu = db.Column(LONGTEXT)
    auteur_id = db.Column(db.String(36), db.ForeignKey('ProfessionnelSante.id'))
    dossier_id = db.Column(db.String(36), db.ForeignKey('DossierMedical.id'))
    traitements = db.relationship('Traitement', backref='compte_rendu', lazy=True)

class Traitement(db.Model):
    __tablename__ = 'Traitement'
    id = db.Column(db.String(36), primary_key=True)
    description = db.Column(LONGTEXT)
    medicament = db.Column(db.String(100))
    posologie = db.Column(db.String(100))
    duree = db.Column(db.String(100))
    compte_rendu_id = db.Column(db.String(36), db.ForeignKey('CompteRendu.id'))

class GouvernanceDesDonnees(db.Model):
    __tablename__ = 'GouvernanceDesDonnees'
    id = db.Column(db.String(36), primary_key=True)
    regles_partage = db.Column(LONGTEXT)
    politique_acces = db.Column(LONGTEXT)

class APIInteroperable(db.Model):
    __tablename__ = 'APIInteroperable'
    id = db.Column(db.String(36), primary_key=True)
    dossier_id = db.Column(db.String(36), db.ForeignKey('DossierMedical.id'))
    cible_etablissement_id = db.Column(db.String(36), db.ForeignKey('Etablissement.id'))
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
