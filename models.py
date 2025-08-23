from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

db=SQLAlchemy()

#User class
class User(db.Model,UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    name = db.Column(db.String, nullable=True)
    password_hash = db.Column(db.String(128)) 
    def set_password(self, password):
        # Use a strong password hashing library like werkzeug.security
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#Admin class
class Admin(db.Model,UserMixin):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    def is_active(self):
        return True 

#Parking Lot class
class Lot(db.Model):
    __tablename__='lot'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(6), nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)

# Parking spot class
class Spot(db.Model):
    __tablename__ = 'spot'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')

    # Relationship to access the parent ParkingLot
    lot = db.relationship('Lot', backref=db.backref('spots', lazy=True))

class Reservation(db.Model):
    __tablename__ = 'reservation'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True) 
    parking_cost_per_unit = db.Column(db.Float, nullable=False)
    # Relationships
    spot = db.relationship('Spot', backref=db.backref('reservations', lazy=True))
    user = db.relationship('User', backref=db.backref('reservations', lazy=True))