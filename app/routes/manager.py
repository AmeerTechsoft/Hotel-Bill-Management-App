from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import User, Client, Room, Service, Transaction, Category
from app import db, mail
from app.utils.decorators import role_required, generate_password
from flask_mail import Message
from werkzeug.security import generate_password_hash

bp = Blueprint('manager', __name__, url_prefix='/manager')

# Manager Dashboard
@bp.route('/dashboard')
@login_required
@role_required('manager')
def dashboard():
    # Fetch all records
    clients = Client.query.all()
    rooms = Room.query.all()
    services = Service.query.all()
    transactions = Transaction.query.all()
    users = User.query.all()
    categories = Category.query.all()

    # Calculate income
    today = datetime.utcnow().date()
    daily_income = sum(t.total_price for t in transactions if t.date.date() == today)
    weekly_income = sum(t.total_price for t in transactions if t.date.date() >= today - timedelta(days=7))
    monthly_income = sum(t.total_price for t in transactions if t.date.date() >= today.replace(day=1))

    # Calculate room status counts
    available_rooms = sum(1 for r in rooms if r.status == 'available')
    occupied_rooms = sum(1 for r in rooms if r.status == 'occupied')
    maintenance_rooms = sum(1 for r in rooms if r.status == 'maintenance')

    return render_template('manager/dashboard.html', 
                           clients=clients, 
                           rooms=rooms, 
                           services=services, 
                           transactions=transactions, 
                           users=users, 
                           categories=categories,
                           daily_income=daily_income,
                           weekly_income=weekly_income,
                           monthly_income=monthly_income,
                           available_rooms=available_rooms,
                           occupied_rooms=occupied_rooms,
                           maintenance_rooms=maintenance_rooms)



# Manage Users
@bp.route('/users')
@login_required
@role_required('manager')
def manage_users():
    users = User.query.all()
    return render_template('manager/manage_users.html', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        contact_number = request.form['contact_number']
        address = request.form['address']
        
        # Convert date_of_birth to a Python date object
        date_of_birth_str = request.form['date_of_birth']
        date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        
        role = request.form['role']
        password = generate_password()
        
        hashed_password = generate_password_hash(password)

        user = User(username=username, email=email, first_name=first_name,
                    last_name=last_name, contact_number=contact_number,
                    address=address, date_of_birth=date_of_birth, role=role,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        # Send password to user email
        msg = Message('Your account credentials', sender='noreply@yourdomain.com', recipients=[email])
        msg.body = f'Your username: {username}\nYour password: {password}'
        mail.send(msg)
        
        flash('User added successfully', 'success')
        return redirect(url_for('manager.manage_users'))
    
    return render_template('manager/add_user.html')

@bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.contact_number = request.form['contact_number']
        user.address = request.form['address']
        date_of_birth_str = request.form['date_of_birth']
        user.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
       
        user.role = request.form['role']
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('manager.manage_users'))
    return render_template('manager/edit_user.html', user=user)

@bp.route('/users/generate_password/<int:user_id>', methods=['GET'])
@login_required
@role_required('manager')
def generate_new_password(user_id):
    user = User.query.get_or_404(user_id)
    
    # Generate new password
    new_password = generate_password()
    
    # Hash the password
    hashed_password = generate_password_hash(new_password)
    
    # Update the user's password in the database
    user.password = hashed_password
    db.session.commit()
    
    # Send the new password to the user's email
    msg = Message('Your new password', sender='Ameer Adeigbe', recipients=[user.email])
    msg.body = f'Your new password is: {new_password}'
    mail.send(msg)
    
    flash('A new password has been generated and sent to the user\'s email.', 'success')
    return redirect(url_for('manager.edit_user', user_id=user.id))


@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('manager')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('manager.manage_users'))

# Manage Clients
@bp.route('/clients')
@login_required
@role_required('manager')
def manage_clients():
    clients = Client.query.all()
    return render_template('manager/manage_clients.html', clients=clients)

@bp.route('/clients/add', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def add_client():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        contact_number = request.form['contact_number']
        email = request.form['email']
        address = request.form['address']

        client = Client(first_name=first_name, last_name=last_name, contact_number=contact_number,
                        email=email, address=address)
        db.session.add(client)
        db.session.commit()
        flash('Client added successfully', 'success')
        return redirect(url_for('manager.manage_clients'))
    return render_template('manager/add_client.html')

@bp.route('/clients/edit/<int:client_id>', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        client.first_name = request.form['first_name']
        client.last_name = request.form['last_name']
        client.contact_number = request.form['contact_number']
        client.email = request.form['email']
        client.address = request.form['address']

        db.session.commit()
        flash('Client updated successfully', 'success')
        return redirect(url_for('manager.manage_clients'))
    return render_template('manager/edit_client.html', client=client)

@bp.route('/clients/delete/<int:client_id>', methods=['POST'])
@login_required
@role_required('manager')
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted successfully', 'success')
    return redirect(url_for('manager.manage_clients'))

# Manage Rooms
@bp.route('/rooms')
@login_required
@role_required('manager')
def manage_rooms():
    rooms = Room.query.all()
    return render_template('manager/manage_rooms.html', rooms=rooms)

@bp.route('/rooms/add', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def add_room():
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        price_per_night = request.form['price_per_night']
        status = request.form['status']

        room = Room(room_number=room_number, room_type=room_type, price_per_night=price_per_night, status=status)
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully', 'success')
        return redirect(url_for('manager.manage_rooms'))
    return render_template('manager/add_room.html')

@bp.route('/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    if request.method == 'POST':
        room.room_number = request.form['room_number']
        room.room_type = request.form['room_type']
        room.price_per_night = request.form['price_per_night']
        room.status = request.form['status']

        db.session.commit()
        flash('Room updated successfully', 'success')
        return redirect(url_for('manager.manage_rooms'))
    return render_template('manager/edit_room.html', room=room)

@bp.route('/rooms/delete/<int:room_id>', methods=['POST'])
@login_required
@role_required('manager')
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted successfully', 'success')
    return redirect(url_for('manager.manage_rooms'))

# Manage Services
@bp.route('/services')
@login_required
@role_required('manager')
def manage_services():
    services = Service.query.all()
    return render_template('manager/manage_services.html', services=services)

@bp.route('/services/add', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def add_service():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        category_id = request.form['category_id']

        service = Service(name=name, price=price, description=description, category_id=category_id)
        db.session.add(service)
        db.session.commit()
        flash('Service added successfully', 'success')
        return redirect(url_for('manager.manage_services'))
    return render_template('manager/add_service.html', categories=categories)

@bp.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    categories = Category.query.all()
    if request.method == 'POST':
        service.name = request.form['name']
        service.price = request.form['price']
        service.description = request.form['description']
        service.category_id = request.form['category_id']

        db.session.commit()
        flash('Service updated successfully', 'success')
        return redirect(url_for('manager.manage_services'))
    return render_template('manager/edit_service.html', service=service, categories=categories)

@bp.route('/services/delete/<int:service_id>', methods=['POST'])
@login_required
@role_required('manager')
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully', 'success')
    return redirect(url_for('manager.manage_services'))


# Manage Categories
@bp.route('/categories')
@login_required
@role_required('manager')
def manage_categories():
    categories = Category.query.all()
    return render_template('manager/manage_categories.html', categories=categories)

@bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully', 'success')
        return redirect(url_for('manager.manage_categories'))
    return render_template('manager/add_category.html')

@bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        category.name = request.form['name']
        category.description = request.form['description']

        db.session.commit()
        flash('Category updated successfully', 'success')
        return redirect(url_for('manager.manage_categories'))
    return render_template('manager/edit_category.html', category=category)

@bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@role_required('manager')
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully', 'success')
    return redirect(url_for('manager.manage_categories'))

@bp.route('/transactions')
@login_required
@role_required('manager')
def manage_transactions():
    # Group transactions by client
    transactions = {}
    clients = Client.query.all()
    for client in clients:
        client_transactions = Transaction.query.filter_by(client_id=client.id).all()
        if client_transactions:
            transactions[client] = client_transactions
    return render_template('manager/manage_transactions.html', transactions=transactions)

@bp.route('/transactions/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    clients = Client.query.all()
    rooms = Room.query.all()
    services = Service.query.all()

    if request.method == 'POST':
        transaction.client_id = request.form['client_id']
        transaction.room_id = request.form['room_id']
        transaction.service_id = request.form['service_id']
        transaction.quantity = request.form['quantity']
        transaction.total_price = request.form['total_price']
        transaction.check_in = request.form['check_in']
        transaction.check_out = request.form['check_out']

        db.session.commit()
        flash('Transaction updated successfully', 'success')
        return redirect(url_for('manager.manage_transactions'))
    
    return render_template('manager/edit_transaction.html', transaction=transaction, 
                           clients=clients, rooms=rooms, services=services)

@bp.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
@login_required
@role_required('manager')
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully', 'success')
    return redirect(url_for('manager.manage_transactions'))


# Confirm Payments and Update Room Status
@bp.route('/confirm_payment/<int:transaction_id>', methods=['POST'])
@login_required
@role_required('manager')
def confirm_payment(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    # Confirm payment logic here
    if transaction.room:
        transaction.room.status = 'cleaning'  # Automatically update room status to 'cleaning'
        db.session.commit()
    flash('Payment confirmed and room status updated', 'success')
    return redirect(url_for('manager.manage_transactions'))
