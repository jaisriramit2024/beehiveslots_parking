from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False) # Owner / Driver
    password_hash = db.Column(db.String(200), nullable=False)
    wallet_balance = db.Column(db.Integer, default=0)
    
    # Relationships
    slots = db.relationship('Slot', backref='owner_user', lazy=True)
    bookings = db.relationship('Booking', backref='driver_user', lazy=True)
    parking_lots = db.relationship('ParkingLot', backref='owner_user_lot', lazy=True)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=True, index=True)  # e.g. 'Chennai'
    full_address = db.Column(db.String(400), nullable=True)       # e.g. '45 Anna Salai, Chennai'
    location = db.Column(db.String(300), nullable=False)          # legacy / fallback
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False, default=1)
    vehicle_type = db.Column(db.String(10), nullable=False, default='car')  # 'car', 'bike', 'both'
    price = db.Column(db.Integer, nullable=True)                  # price per hour (optional)
    image_filename = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    
    bookings = db.relationship('Booking', backref='slot_ref', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Active') # Active, Completed
    total_cost = db.Column(db.Integer)

class ParkingLotBooking(db.Model):
    """Booking against a ParkingLot (new-style lots with full details)."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    duration_hours = db.Column(db.Integer, nullable=False, default=1)
    amount_paid = db.Column(db.Integer, nullable=False, default=0)
    booked_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Confirmed')  # Confirmed, Cancelled

    user = db.relationship('User', foreign_keys=[user_id])
    lot  = db.relationship('ParkingLot', foreign_keys=[lot_id])
