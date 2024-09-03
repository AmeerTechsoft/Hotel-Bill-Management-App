from functools import wraps
from flask import abort
from flask_login import current_user
import string
import random

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role_name:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Specifically for admin access
def admin_required(f):
    return role_required('Admin')(f)

def manager_required(f):
    return role_required('Manager')(f)

def staff_required(f):
    return role_required('Staff')(f)

# Generate random password
def generate_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))