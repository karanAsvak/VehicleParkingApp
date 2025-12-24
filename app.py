from flask import Flask, request, render_template, session, url_for, redirect, flash
from models import db, User, Admin, Lot, Spot, Reservation
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_mail import Mail, Message
import os

app = Flask(__name__, instance_relative_config=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SECRET_KEY'] = 'a-very-secret-and-unique-key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS") == "True"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

app.config["MAIL_DEFAULT_SENDER"] = (
    "Vehicle Parking App",
    os.getenv("MAIL_USERNAME")
)


mail = Mail(app)

db.init_app(app)

# Create all tables in the database
with app.app_context():
    db.create_all()
    try:
        admin = Admin(username='admin', password=generate_password_hash('adminpass'))
        db.session.add(admin)
        db.session.commit() 
    except:
        db.session.rollback()

# Email notification functions
def send_booking_confirmation_email(user, reservation, spot, lot):
    """Send email confirmation when spot is booked"""
    try:
        msg = Message(
            subject='Parking Spot Booking Confirmation',
            recipients=[user.email]
        )
        
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px;">Booking Confirmation</h2>
                
                <p>Dear <strong>{user.name}</strong>,</p>
                
                <p>Your parking spot has been successfully booked!</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin-top: 0;">Booking Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0;"><strong>Spot Number:</strong></td>
                            <td style="padding: 8px 0;">{spot.id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Location:</strong></td>
                            <td style="padding: 8px 0;">{lot.prime_location_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Address:</strong></td>
                            <td style="padding: 8px 0;">{lot.address}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Vehicle Number:</strong></td>
                            <td style="padding: 8px 0;"><strong>{reservation.vehicle_number}</strong></td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Vehicle Type:</strong></td>
                            <td style="padding: 8px 0;">{reservation.vehicle_type}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Parking Time:</strong></td>
                            <td style="padding: 8px 0;">{reservation.parking_timestamp.strftime('%d %b %Y, %I:%M %p')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Rate:</strong></td>
                            <td style="padding: 8px 0;">₹{reservation.parking_cost_per_unit}/hour</td>
                        </tr>
                    </table>
                </div>
                
                <p style="color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px;">
                    <strong>Note:</strong> Please remember to release your spot when you leave to avoid extra charges.
                </p>
                
                <p>Thank you for using our parking service!</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #6c757d;">This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending booking confirmation email: {e}")
        return False

def send_release_notification_email(user, reservation, spot, lot, total_cost, duration_hours):
    """Send email notification when spot is released with total cost"""
    try:
        msg = Message(
            subject='Parking Spot Released - Payment Summary',
            recipients=[user.email]
        )
        
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #dc3545; border-bottom: 2px solid #dc3545; padding-bottom: 10px;">Parking Spot Released</h2>
                
                <p>Dear <strong>{user.name}</strong>,</p>
                
                <p>Your parking spot has been released successfully. Here are the complete details:</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #007bff; margin-top: 0;">Parking Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0;"><strong>Spot Number:</strong></td>
                            <td style="padding: 8px 0;">{spot.id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Location:</strong></td>
                            <td style="padding: 8px 0;">{lot.prime_location_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Address:</strong></td>
                            <td style="padding: 8px 0;">{lot.address}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Vehicle Number:</strong></td>
                            <td style="padding: 8px 0;"><strong>{reservation.vehicle_number}</strong></td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Vehicle Type:</strong></td>
                            <td style="padding: 8px 0;">{reservation.vehicle_type}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #0056b3; margin-top: 0;">Time & Payment Summary</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0;"><strong>Check-in:</strong></td>
                            <td style="padding: 8px 0;">{reservation.parking_timestamp.strftime('%d %b %Y, %I:%M %p')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Check-out:</strong></td>
                            <td style="padding: 8px 0;">{reservation.leaving_timestamp.strftime('%d %b %Y, %I:%M %p')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Duration:</strong></td>
                            <td style="padding: 8px 0;">{duration_hours:.2f} hours</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Rate:</strong></td>
                            <td style="padding: 8px 0;">₹{reservation.parking_cost_per_unit}/hour</td>
                        </tr>
                        <tr style="border-top: 2px solid #007bff;">
                            <td style="padding: 12px 0; font-size: 18px;"><strong>Total Cost:</strong></td>
                            <td style="padding: 12px 0; font-size: 18px; color: #28a745;"><strong>₹{total_cost:.2f}</strong></td>
                        </tr>
                    </table>
                </div>
                
                <p style="color: #155724; background-color: #d4edda; padding: 10px; border-radius: 5px;">
                    <strong>Thank you!</strong> We hope you had a pleasant parking experience.
                </p>
                
                <p>If you have any questions or concerns about this transaction, please contact our support team.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #6c757d;">This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending release notification email: {e}")
        return False 

# Helper functions for session management
def is_logged_in():
    """Check if any user is logged in"""
    return 'user_id' in session and 'role' in session

def logged_admin(user_id):
    """Check if the logged in user is admin and matches the user_id"""
    if 'user_id' in session and session['user_id'] == user_id:
        admin = Admin.query.filter_by(id=user_id).first()
        if admin:
            return True
    return False

def logged_user(user_id):
    """Check if the logged in user matches the user_id"""
    if 'user_id' in session and session['user_id'] == user_id:
        user = User.query.filter_by(id=user_id).first()
        if user:
            return True
    return False

def get_current_user():
    """Get current logged in user object"""
    if not is_logged_in():
        return None
    if session.get('role') == 'admin':
        return db.session.get(Admin, session['user_id'])
    else:
        return db.session.get(User, session['user_id'])

@app.route('/', methods=['GET', 'POST'])
def login():
    """User and Admin Login Route"""
    # Redirect if already logged in
    if is_logged_in():
        if session.get('role') == 'admin':
            return redirect(url_for('admin', id=session['user_id']))
        else:
            return redirect(url_for('user', id=session['user_id']))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if admin
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['user_id'] = admin.id
            session['role'] = 'admin'
            session['username'] = admin.username
            flash('Welcome Admin!', 'success')
            return redirect(url_for('admin', id=admin.id))
        
        # Check if user
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = 'user'
            session['username'] = user.username
            session['name'] = user.name
            flash(f'Welcome {user.name}!', 'success')
            return redirect(url_for('user', id=user.id))
        else:
            flash('Invalid username or password', 'danger')
            return render_template('/auth/login.html', error=True)

    return render_template('/auth/login.html', error=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration Route"""
    # Redirect if already logged in
    if is_logged_in():
        if session.get('role') == 'admin':
            return redirect(url_for('admin', id=session['user_id']))
        else:
            return redirect(url_for('user', id=session['user_id']))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form.get('email', '')
        name = request.form['name']
        pincode = request.form['pincode']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return render_template('/auth/register.html', error=True)
        
        # Create new user
        new_user = User(
            username=username,
            name=name,
            email=email,
            pincode=pincode
        )   
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('/auth/register.html', error=False)


@app.route('/admin/<int:id>')
def admin(id):
    """Admin Dashboard - View all parking lots and spots"""
    if not logged_admin(id):
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('login'))
    
    lots = Lot.query.all()
    lot_spots = []
    for lot in lots:
        container = [[lot.id, lot.prime_location_name, lot.address, lot.price]]
        spots = Spot.query.filter_by(lot_id=lot.id).all()
        occupied = False
        for spot in spots:
            container.append([spot.id, spot.status, spot.vehicle_type])
            if spot.status == 'O':
                occupied = True
        container.append(occupied)
        lot_spots.append(container)
    return render_template('admin_home.html', active_tab='home', lot_spots=lot_spots)

@app.route('/viewSpot')
def view_spot():
    """View details of a specific parking spot"""
    if 'user_id' not in session or not logged_admin(session['user_id']):
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('login'))
    
    spot_id = request.args.get('id')
    status = request.args.get('status')
    
    # Get spot details
    spot = db.session.get(Spot, spot_id)
    
    # Get booking/reservation details if spot is occupied
    booking_info = None
    if spot and status in ['O', 'R']:
        reservation = Reservation.query.filter_by(spot_id=spot_id, leaving_timestamp=None).first()
        if reservation:
            user = db.session.get(User, reservation.user_id)
            booking_info = {
                'vehicle_number': reservation.vehicle_number,
                'vehicle_type': reservation.vehicle_type,
                'user_name': user.name if user else 'Unknown',
                'parking_timestamp': reservation.parking_timestamp,
                'cost_per_hour': reservation.parking_cost_per_unit
            }
    
    return render_template('view_spot.html', id=spot_id, status=status, spot=spot, booking_info=booking_info)

@app.route('/deleteSpot')
def delete_spot():
    """Delete a parking spot"""
    if 'user_id' not in session or not logged_admin(session['user_id']):
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('login'))
    
    spot_id = request.args.get('id')
    spot = db.session.get(Spot, spot_id)
    if spot:
        # Check if spot is occupied
        reservation = Reservation.query.filter_by(spot_id=spot_id, leaving_timestamp=None).first()
        if not reservation:
            db.session.delete(spot)
            db.session.commit()
            flash('Spot deleted successfully', 'success')
        else:
            flash('Cannot delete an occupied spot', 'danger')
    return redirect(url_for('admin', id=session['user_id']))

def get_next_available_spot_ids(count):
    """Get the next available spot IDs, reusing deleted IDs if possible"""
    # Get all existing spot IDs
    existing_ids = set(spot.id for spot in Spot.query.with_entities(Spot.id).all())
    
    available_ids = []
    current_id = 1
    
    # First, try to reuse gaps in the sequence
    while len(available_ids) < count:
        if current_id not in existing_ids:
            available_ids.append(current_id)
        current_id += 1
    
    return available_ids

@app.route('/addLot', methods=['GET', 'POST'])
def add_lot():
    """Add a new parking lot with multiple spots"""
    if 'user_id' not in session or not logged_admin(session['user_id']):
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        location = request.form['location']
        price = request.form['price']
        address = request.form['address']
        pincode = request.form['pincode']
        two_wheeler_spots = int(request.form['two_wheeler_spots'])
        four_wheeler_spots = int(request.form['four_wheeler_spots'])
        
        maxspot = two_wheeler_spots + four_wheeler_spots
        
        if maxspot == 0:
            flash('Total spots must be greater than 0', 'danger')
            return render_template('add_lot.html')
        
        lot = Lot(
            prime_location_name=location,
            price=float(price),
            address=address,
            pin_code=pincode,
            maximum_number_of_spots=maxspot
        )
        db.session.add(lot)
        db.session.flush()
        
        # Get available spot IDs (reusing deleted IDs)
        spot_ids = get_next_available_spot_ids(maxspot)
        
        # Create parking spots for this lot with specific IDs
        spots = []
        spot_index = 0
        
        # Add two-wheeler spots
        for i in range(two_wheeler_spots):
            spot = Spot(id=spot_ids[spot_index], lot_id=lot.id, status='A', vehicle_type='Two-Wheeler')
            spots.append(spot)
            spot_index += 1
        
        # Add four-wheeler spots
        for i in range(four_wheeler_spots):
            spot = Spot(id=spot_ids[spot_index], lot_id=lot.id, status='A', vehicle_type='Four-Wheeler')
            spots.append(spot)
            spot_index += 1
            
        db.session.add_all(spots)
        db.session.commit()
        flash(f'Lot added with {two_wheeler_spots} two-wheeler and {four_wheeler_spots} four-wheeler spots', 'success')
        return redirect(url_for('admin', id=session['user_id']))
    
    return render_template('add_lot.html')

@app.route('/delete_lot')
def delete_lot():
    """Delete a parking lot and all its spots"""
    if 'user_id' not in session or not logged_admin(session['user_id']):
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('login'))
    
    lot_id = request.args.get('id')
    
    # Check if any spots in this lot have active reservations (not yet released)
    spots_with_active_reservations = db.session.query(Spot).join(Reservation).filter(
        Spot.lot_id == lot_id,
        Reservation.leaving_timestamp == None  # Only check for active reservations
    ).all()
    
    if spots_with_active_reservations:
        flash('Cannot delete lot with existing reservations. Please wait for all bookings to complete.', 'danger')
        return redirect(url_for('admin', id=session['user_id']))
    
    # Check if any spots are occupied
    occupied_spots = Spot.query.filter(
        Spot.lot_id == lot_id,
        Spot.status == 'O'
    ).all()
    
    if occupied_spots:
        flash('Cannot delete lot with occupied spots', 'danger')
        return redirect(url_for('admin', id=session['user_id']))
    
    db.session.query(Spot).filter(Spot.lot_id == lot_id).delete()
    db.session.query(Lot).filter(Lot.id == lot_id).delete()
    db.session.commit()
    flash('Lot deleted successfully', 'success')
    return redirect(url_for('admin', id=session['user_id']))

@app.route('/edit_lot', methods=['GET', 'POST'])
def edit_lot():
    """Edit parking lot - modify number of spots"""
    if 'user_id' not in session or not logged_admin(session['user_id']):
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('login'))
    
    lot_id = request.args.get('id')
    
    if request.method == 'POST':
        maxspot = int(request.form['maxspot'])
        lot = db.session.query(Lot).filter(Lot.id == lot_id).first()
        spots = db.session.query(Spot).filter(Spot.lot_id == lot_id)
        
        current_count = spots.count()
        
        # Update the lot
        lot.maximum_number_of_spots = maxspot
        
        if current_count < maxspot:
            # Increase spots - get available IDs
            needed = maxspot - current_count
            spot_ids = get_next_available_spot_ids(needed)
            for spot_id in spot_ids:
                s = Spot(id=spot_id, lot_id=lot_id, status='A')
                db.session.add(s)
        else:
            # Decrease spots - only delete available ones
            diff = current_count - maxspot
            available = spots.filter(Spot.status == 'A')
            
            if diff > available.count():
                flash('Cannot reduce spots - not enough available spots', 'danger')
                return redirect(url_for('admin', id=session['user_id']))
            
            # Delete the last 'diff' available spots
            query = db.session.query(Spot.id).filter(
                Spot.lot_id == lot_id,
                Spot.status == 'A'
            ).order_by(db.desc(Spot.id)).limit(diff)
            db.session.query(Spot).filter(Spot.id.in_(query)).delete(synchronize_session='fetch')
        
        db.session.commit()
        flash('Lot updated successfully', 'success')
        return redirect(url_for('admin', id=session['user_id']))
    
    lot = db.session.get(Lot, lot_id)
    return render_template('edit_lot.html', id=lot_id, lot=lot)

@app.route('/admin/search', methods=['GET', 'POST'])
def admin_search():
    """Admin search for users and their bookings"""
    if 'user_id' not in session or not logged_admin(session['user_id']):
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('login'))
    
    results = []
    search_query = ''
    
    if request.method == 'POST':
        search_query = request.form.get('search', '')
        # Search for users
        users = User.query.filter(
            (User.username.contains(search_query)) | 
            (User.name.contains(search_query)) |
            (User.pincode.contains(search_query))
        ).all()
        results = users
    
    return render_template('admin_search.html', active_tab='search', results=results, query=search_query)

@app.route('/admin/summary')
def admin_summary():
    """Admin summary - statistics and booking history"""
    if 'user_id' not in session or not logged_admin(session['user_id']):
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('login'))
    
    total_lots = Lot.query.count()
    total_spots = Spot.query.count()
    available_spots = Spot.query.filter_by(status='A').count()
    occupied_spots = Spot.query.filter_by(status='O').count()
    reserved_spots = Spot.query.filter_by(status='R').count()
    
    # Get all reservations
    reservations = Reservation.query.all()
    
    stats = {
        'total_lots': total_lots,
        'total_spots': total_spots,
        'available': available_spots,
        'occupied': occupied_spots,
        'reserved': reserved_spots,
        'occupancy_rate': round((occupied_spots / total_spots * 100) if total_spots > 0 else 0, 2)
    }
    
    return render_template('admin_summary.html', active_tab='summary', stats=stats, reservations=reservations)

@app.route('/user/<int:id>', methods=['GET', 'POST'])
def user(id):
    """User Dashboard - Browse and search parking lots"""
    if not logged_user(id):
        flash('Please login as user to access this page.', 'danger')
        return redirect(url_for('login'))
    
    current_user = get_current_user()
    lot_spot = []
    location = ''
    
    if request.method == 'POST':
        location = request.form.get('loc', '')
        # Search by location name or pincode
        lot_spot = db.session.query(Lot, Spot).join(
            Spot, Lot.id == Spot.lot_id
        ).filter(
            db.or_(
                Lot.prime_location_name.ilike(f'%{location}%'),
                Lot.pin_code.contains(location)
            )
        ).all()
    
    return render_template('user_home.html', user=current_user.name, active_tab='home', lot_spot=lot_spot, location=location)

@app.route('/book_spot', methods=['POST'])
def book_spot():
    """Book a parking spot"""
    if 'user_id' not in session or not logged_user(session['user_id']):
        flash('Please login to book a spot.', 'danger')
        return redirect(url_for('login'))
    
    current_user = get_current_user()
    spot_id = request.form.get('spot_id')
    lot_id = request.form.get('lot_id')
    vehicle_number = request.form.get('vehicle_number')
    vehicle_type = request.form.get('vehicle_type')
    
    # Validate inputs
    if not vehicle_number or not vehicle_type:
        flash('Vehicle number and type are required', 'danger')
        return redirect(url_for('user', id=session['user_id']))
    
    spot = db.session.get(Spot, spot_id)
    lot = db.session.get(Lot, lot_id)
    
    if not spot or not lot:
        flash('Invalid spot or lot', 'danger')
        return redirect(url_for('user', id=session['user_id']))
    
    if spot.status != 'A':
        flash('This spot is not available', 'danger')
        return redirect(url_for('user', id=session['user_id']))
    
    # Verify vehicle type matches spot type
    if spot.vehicle_type != vehicle_type:
        flash(f'This spot is for {spot.vehicle_type} only', 'danger')
        return redirect(url_for('user', id=session['user_id']))
    
    # Check if user already has an active booking
    active_booking = Reservation.query.filter_by(
        user_id=current_user.id,
        leaving_timestamp=None
    ).first()
    
    if active_booking:
        flash('You already have an active booking. Release it first.', 'warning')
        return redirect(url_for('user', id=session['user_id']))
    
    # Create reservation
    reservation = Reservation(
        spot_id=spot_id,
        user_id=current_user.id,
        parking_timestamp=datetime.now(),
        parking_cost_per_unit=lot.price,
        vehicle_number=vehicle_number.upper(),
        vehicle_type=vehicle_type
    )
    
    # Update spot status
    spot.status = 'O'  # O = Occupied
    
    db.session.add(reservation)
    db.session.commit()
    
    # Send booking confirmation email
    if current_user.email:
        send_booking_confirmation_email(current_user, reservation, spot, lot)
    
    flash(f'Successfully booked spot {spot_id}', 'success')
    return redirect(url_for('user', id=session['user_id']))

@app.route('/release_spot', methods=['GET', 'POST'])
def release_spot():
    """Release a booked parking spot"""
    if 'user_id' not in session or not logged_user(session['user_id']):
        flash('Please login to release a spot.', 'danger')
        return redirect(url_for('login'))
    
    current_user = get_current_user()
    
    if request.method == 'POST':
        reservation_id = request.form.get('reservation_id')
        
        reservation = db.session.get(Reservation, reservation_id)
        if not reservation:
            flash('Reservation not found', 'danger')
            return redirect(url_for('user_summary'))
        
        if reservation.user_id != current_user.id:
            flash('Unauthorized', 'danger')
            return redirect(url_for('user_summary'))
        
        # Update reservation
        reservation.leaving_timestamp = datetime.now()
        
        # Calculate duration and total cost
        duration = reservation.leaving_timestamp - reservation.parking_timestamp
        duration_hours = duration.total_seconds() / 3600  # Convert to hours
        total_cost = duration_hours * reservation.parking_cost_per_unit
        
        # Get lot and spot details for email
        spot = db.session.get(Spot, reservation.spot_id)
        lot = db.session.get(Lot, spot.lot_id)
        
        # Update spot status back to available
        spot.status = 'A'  # A = Available
        
        db.session.commit()
        
        # Send release notification email with cost details
        if current_user.email:
            send_release_notification_email(current_user, reservation, spot, lot, total_cost, duration_hours)
        
        flash(f'Spot released successfully. Total cost: ₹{total_cost:.2f}', 'success')
        return redirect(url_for('user_summary'))
    
    return redirect(url_for('user_summary'))

@app.route('/user/summary')
def user_summary():
    """User Booking Summary - View booking history"""
    if 'user_id' not in session or not logged_user(session['user_id']):
        flash('Please login to view your bookings.', 'danger')
        return redirect(url_for('login'))
    
    current_user = get_current_user()
    # Get all reservations for current user
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    
    return render_template('user_summary.html', active_tab='summary', user=current_user.name, reservations=reservations)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/edit')
def edit_profile():
    """Edit user profile - placeholder"""
    if not is_logged_in():
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    
    current_user = get_current_user()
    return render_template('edit_profile.html', user=current_user)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.debug = True
    app.run()

