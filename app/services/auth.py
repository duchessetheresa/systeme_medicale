import uuid
from werkzeug.security import generate_password_hash, check_password_hash

def generate_user_id():
    return str(uuid.uuid4())

def verify_password(stored_hash, provided_password):
    return check_password_hash(stored_hash, provided_password)

def get_password_hash(password):
    return generate_password_hash(password) 
