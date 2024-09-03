from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Client, Room, Service, Transaction
from app import db
from app.forms import AddClientForm, CheckInForm, ServiceForm, PaymentForm
from app.utils.decorators import role_required
from datetime import datetime

bp = Blueprint('staff', __name__)

@bp.route('/dashboard')
@login_required
@role_required('staff')
def dashboard():
    # Get clients who have no transactions or whose latest transaction has no check_out date
    clients = Client.query.filter(
        Client.transactions == None  # No transactions, i.e., not checked in
    ).union(
        Client.query.filter(
            Client.transactions.any(Transaction.check_out == None)
        )
    ).all()
    
    rooms = Room.query.all()
    return render_template('staff/dashboard.html', clients=clients, rooms=rooms)



@bp.route('/add-client', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def add_client():
    form = AddClientForm()
    if form.validate_on_submit():
        client = Client(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            contact_number=form.contact_number.data,
            email=form.email.data,
            address=form.address.data
        )
        db.session.add(client)
        db.session.commit()
        flash('Client added successfully!', 'success')
        return redirect(url_for('staff.dashboard'))
    return render_template('staff/add_client.html', form=form)


@bp.route('/check-in/<int:client_id>', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def check_in(client_id):
    client = Client.query.get_or_404(client_id)
    
    # Check if the client has an ongoing transaction (i.e., not checked out)
    active_transaction = Transaction.query.filter(
        Transaction.client_id == client.id,
        Transaction.check_out.is_(None)
    ).first()

    if active_transaction:
        flash('Client is already checked in.', 'warning')
        return redirect(url_for('staff.dashboard'))

    form = CheckInForm()
    form.room_id.choices = [(room.id, room.room_number) for room in Room.query.filter_by(status='Available').all()]
    
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    if form.validate_on_submit():
        room = Room.query.get(form.room_id.data)
        room.status = 'Occupied'
        transaction = Transaction(
            client_id=client.id,
            room_id=room.id,
            check_in=form.check_in.data,
            total_price=room.price_per_night * form.nights.data
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Client checked in successfully!', 'success')
        return redirect(url_for('staff.dashboard'))
    
    return render_template('staff/check_in.html', form=form, client=client, current_time=current_time)

    
@bp.route('/client/<int:client_id>')
@login_required
@role_required('staff')
def client_details(client_id):
    client = Client.query.get_or_404(client_id)
    # Query for the latest transaction with room information if needed
    latest_transaction = Transaction.query.filter_by(client_id=client.id).first()
    print(latest_transaction)
    # Fetch all transactions for the client including service transactions
    service_transactions = Transaction.query.filter_by(client_id=client.id).filter(Transaction.service_id.isnot(None)).all()
    
    return render_template('staff/client_details.html', client=client, latest_transaction=latest_transaction, service_transactions=service_transactions)



@bp.route('/client/<int:client_id>/checkout', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def check_out(client_id):
    client = Client.query.get_or_404(client_id)
    
    # Get all transactions for the client
    transactions = Transaction.query.filter_by(client_id=client.id, check_out=None).all()
    
    # Calculate the total amount
    total_amount = sum(t.total_price for t in transactions)
    
    if request.method == 'POST':
        # Logic to confirm payment (e.g., by card or manually)
        # Here, you should add code to handle payment confirmation (e.g., integrating with external payment systems)
        
        # Mark all transactions as checked out and update room status
        for transaction in transactions:
            if transaction.room:
                # Update the room status to 'Cleaning' or 'Maintained'
                transaction.room.status = 'Cleaning'  # or 'Maintained', based on your business logic
                db.session.add(transaction.room)
            transaction.check_out = datetime.utcnow()
            db.session.add(transaction)
        
        db.session.commit()
        
        flash('Checkout complete. All transactions have been marked as checked out, and room status has been updated.', 'success')
        return redirect(url_for('staff.client_details', client_id=client.id))
    
    return render_template('staff/checkout.html', client=client, transactions=transactions, total_amount=total_amount)

@bp.route('/client/<int:client_id>/remove_service/<int:transaction_id>', methods=['POST'])
@login_required
@role_required('staff')
def remove_service(client_id, transaction_id):
    # Get the client and transaction
    client = Client.query.get_or_404(client_id)
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Ensure the transaction belongs to the client
    if transaction.client_id != client.id:
        flash('Transaction not found for this client.', 'danger')
        return redirect(url_for('staff.client_details', client_id=client.id))
    
    # Remove the transaction
    db.session.delete(transaction)
    db.session.commit()
    
    flash('Service removed successfully!', 'success')
    return redirect(url_for('staff.client_details', client_id=client.id))




@bp.route('/add-service/<int:client_id>', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def add_service(client_id):
    client = Client.query.get_or_404(client_id)
    
    # Check if the client has an active (not checked out) transaction
    active_transaction = next((tx for tx in client.transactions if tx.check_out is None), None)
    if not active_transaction:
        flash('Client is not checked in or has already checked out.', 'warning')
        return redirect(url_for('staff.dashboard'))

    form = ServiceForm()
    form.service_id.choices = [(service.id, f"{service.name} {service.description} (₦ {service.price})") for service in Service.query.all()]
    
    if form.validate_on_submit():
        service = Service.query.get_or_404(form.service_id.data)
        transaction = Transaction(
            client_id=client.id,
            service_id=service.id,
            quantity=form.quantity.data,
            total_price=service.price * form.quantity.data
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('staff.client_details'))
    
    return render_template('staff/add_service.html', form=form, client=client)


@bp.route('/confirm-payment/<int:client_id>', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def confirm_payment(client_id):
    client = Client.query.get_or_404(client_id)
    transactions = Transaction.query.filter_by(client_id=client.id, check_out=None).all()
    
    if not transactions:
        flash('Client has already checked out.', 'warning')
        return redirect(url_for('staff.dashboard'))
    
    total_amount = sum(t.total_price for t in transactions)
    form = PaymentForm()
    
    if form.validate_on_submit():
        # Handle payment processing here
        for transaction in transactions:
            transaction.payment_status = 'Paid'  # Mark as paid
            db.session.commit()
        
        flash('Payment confirmed successfully!', 'success')
        return redirect(url_for('staff.dashboard'))
    
    return render_template('staff/confirm_payment.html', form=form, client=client, total_amount=total_amount)


@bp.route('/clients', methods=['GET'])
@login_required
@role_required('staff')
def view_clients():
    search_query = request.args.get('search', '')
    filter_status = request.args.get('status', '')

    query = Client.query

    if search_query:
        query = query.filter(Client.first_name.ilike(f'%{search_query}%') |
                             Client.last_name.ilike(f'%{search_query}%') |
                             Client.email.ilike(f'%{search_query}%'))

    if filter_status:
        if filter_status == 'checked_in':
            query = query.join(Client.transactions).filter(Transaction.check_out.is_(None))
        elif filter_status == 'checked_out':
            query = query.join(Client.transactions).filter(Transaction.check_out.isnot(None))

    clients = query.distinct().all()
    return render_template('staff/view_clients.html', clients=clients, search_query=search_query, filter_status=filter_status)