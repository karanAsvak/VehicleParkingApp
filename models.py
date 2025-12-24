from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# User class
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable=True)
    pincode = db.Column(db.String(6), nullable=False)
    name = db.Column(db.String, nullable=True)
    password_hash = db.Column(db.String(128))
    reservations = db.relationship('Reservation', backref='user', cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash and set password using werkzeug.security"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password_hash, password)

# Admin class
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False) 

#Parking Lot class
class Lot(db.Model):
    __tablename__='lot'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(6), nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)

    spots = db.relationship('Spot', backref='lot',cascade="all, delete-orphan")

# Parking spot class
class Spot(db.Model):
    __tablename__ = 'spot'
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # Manual ID assignment
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # A=Available, O=Occupied, R=Reserved
    vehicle_type = db.Column(db.String(20), nullable=False, default='Two-Wheeler')  # Two-Wheeler or Four-Wheeler

    reservation = db.relationship('Reservation', backref='spot', uselist=False, cascade="all, delete-orphan")
    

class Reservation(db.Model):
    """Booking/Reservation model for parking spots"""
    __tablename__ = 'reservation'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True) 
    parking_cost_per_unit = db.Column(db.Float, nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)  # Vehicle registration number
    vehicle_type = db.Column(db.String(20), nullable=False)  # Two-Wheeler or Four-Wheeler
    
    # Relationships
    