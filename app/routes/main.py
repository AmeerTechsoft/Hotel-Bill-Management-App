from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        elif current_user.role == 'manager':
            return redirect(url_for('manager.dashboard'))
    return render_template('landing.html')
