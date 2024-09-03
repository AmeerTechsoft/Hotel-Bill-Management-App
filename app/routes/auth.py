from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, logout_user, current_user
from app import db, login_manager
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.decorators import admin_required
from app.utils.helpers import send_email
from app.forms import LoginForm


bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def redirect_user_to_dashboard(user):
    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user.role == 'manager':
        return redirect(url_for('manager.dashboard'))
    elif user.role == 'staff':
        return redirect(url_for('staff.dashboard'))
    else:
        return redirect(url_for('main.index'))  # Default redirect if no role matches
    

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect to the appropriate dashboard based on the user's role
        return redirect_user_to_dashboard(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=form.remember_me.data)
            # Redirect to the appropriate dashboard based on the user's role
            return redirect_user_to_dashboard(user)
        else:
            flash('Login Unsuccessful. Please check your username and password.', 'danger')

    return render_template('login.html', form=form)

@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    pass

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        contact_number = request.form['contact_number']
        address = request.form['address']
        date_of_birth = request.form['date_of_birth']
        role = request.form['role']

        new_user = User(username=username, email=email, password=password,
                        first_name=first_name, last_name=last_name,
                        contact_number=contact_number, address=address,
                        date_of_birth=date_of_birth, role=role)

        db.session.add(new_user)
        db.session.commit()

        # Send credentials via email
        send_email(email, username, request.form['password'])

        flash(f'User {username} registered successfully!')
        return redirect(url_for('auth.register'))
    return render_template('register.html')

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        # Check if current password is correct
        if not check_password_hash(current_user.password, current_password):
            flash('Incorrect current password.', 'danger')
            return redirect(url_for('auth.change_password'))

        # Check if new password matches the confirmation
        if new_password != confirm_new_password:
            flash('New password and confirmation do not match.', 'danger')
            return redirect(url_for('auth.change_password'))

        # Update the password
        hashed_password = generate_password_hash(new_password)
        current_user.password = hashed_password
        db.session.commit()

        flash('Password updated successfully!', 'success')
        return redirect(url_for('main.index'))  # Redirect to dashboard or any other page

    return render_template('change_password.html')