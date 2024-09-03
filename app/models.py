from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    contact_number = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    employment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"<User {self.username}, Role: {self.role}>"
    
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    transactions = db.relationship('Transaction', backref='client', lazy=True)

    def __repr__(self):
        return f"<Client {self.first_name} {self.last_name}>"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    services = db.relationship('Service', backref='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)  # e.g., Jollof Rice, Foot Massage
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    transactions = db.relationship('Transaction', backref='service', lazy=True)

    def __repr__(self):
        return f"<Service {self.name} ({self.category.name})>"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    room_type = db.Column(db.String(64), nullable=False)  # e.g., Single, Double, Suite
    price_per_night = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Available')  # Available, Occupied, Maintenance
    transactions = db.relationship('Transaction', backref='room', lazy=True)

    def __repr__(self):
        return f"<Room {self.room_number} ({self.room_type})>"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)  # Nullable for room-only transactions
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)  # Nullable for non-room transactions
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False)
    check_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out = db.Column(db.DateTime, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        if self.room:
            return f"<Transaction Room {self.room.room_number} for {self.client.first_name} from {self.check_in} to {self.check_out}>"
        else:
            return f"<Transaction {self.service.name} x{self.quantity} for {self.client.first_name} on {self.date}>"
