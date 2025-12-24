# Flask-Based Vehicle Parking System

## Project Overview
A comprehensive web-based parking management system developed as a college mini-project for Saveetha Engineering College. This system provides real-time parking slot availability, user registration, booking management, and administrative controls.

## Tech Stack
- **Backend**: Python Flask
- **ORM**: SQLAlchemy
- **Database**: SQLite
- **Templates**: Jinja2
- **Frontend**: HTML + Bootstrap 5 (CDN)
- **Architecture**: Three-Tier Web Architecture

## Features

### 1. User Management
- User registration with secure password hashing
- Login and logout functionality
- Session management using Flask-Login
- Role-based access (User/Admin)

### 2. Parking Slot Management
- Multiple parking lots with configurable spots
- Real-time slot status tracking:
  - **A** (Available)
  - **O** (Occupied)
  - **R** (Reserved)
- Dynamic spot addition/removal

### 3. Booking System
- Search parking lots by location or pincode
- View available parking spots in real-time
- One-click booking functionality
- Automatic occupancy calculation
- Prevents double booking

### 4. Slot Release (Check-out)
- Users can release their booked spots
- Automatic status update to "Available"
- Time tracking for duration calculation

### 5. Admin Dashboard
- View all parking lots and their status
- Add/Edit/Delete parking lots
- Monitor user bookings
- Search users and view their history
- System statistics and summary
- Booking history with timestamps

### 6. User Dashboard
- Search and browse parking lots
- View available spots with visual indicators
- Book parking spots
- View booking history
- Calculate parking costs based on duration

## Database Schema

### User Table
- id (Primary Key)
- username (Unique)
- email
- password_hash
- pincode
- name
- role (user/admin)

### ParkingLot (Lot) Table
- id (Primary Key)
- prime_location_name
- address
- pin_code
- price (hourly rate)
- maximum_number_of_spots

### Spot Table
- id (Primary Key)
- lot_id (Foreign Key)
- status (A/O/R)

### Reservation (Booking) Table
- id (Primary Key)
- user_id (Foreign Key)
- spot_id (Foreign Key)
- parking_timestamp
- leaving_timestamp
- parking_cost_per_unit

### Admin Table
- id (Primary Key)
- username (Unique)
- password

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone/Download the project**
   ```bash
   cd VehicleParkingApp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   The database will be automatically created when you first run the application.

4. **Create default admin (Optional)**
   Open Python shell:
   ```python
   from app import app, db
   from models import Admin
   
   with app.app_context():
       admin = Admin(username='admin', password='admin123')
       db.session.add(admin)
       db.session.commit()
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to: `http://localhost:5000`

## Default Credentials

### Admin
- Username: `admin`
- Password: `admin123` (if you created the default admin)

### Test User
You can register a new user through the registration page.

## Usage Guide

### For Users:
1. Register a new account
2. Login with your credentials
3. Search for parking lots by location/pincode
4. View available spots
5. Click "Book Now" to reserve a spot
6. Go to "My Bookings" to view active and past bookings
7. Release spots when done

### For Admins:
1. Login with admin credentials
2. **Home**: View all parking lots and spot status
3. **Add Lot**: Create new parking lots with multiple spots
4. **Edit**: Modify the number of spots in a lot
5. **Search Users**: Find users by username, name, or pincode
6. **Summary**: View system statistics and booking history

## Project Structure

```
VehicleParkingApp/
│
├── app.py                 # Main Flask application
├── models.py              # Database models (SQLAlchemy)
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
│
├── instance/
│   └── project.db        # SQLite database (auto-generated)
│
├── templates/
│   ├── base.html         # Base template
│   ├── admin_base.html   # Admin base template
│   ├── user_base.html    # User base template
│   ├── admin_home.html   # Admin dashboard
│   ├── admin_search.html # User search page
│   ├── admin_summary.html# Statistics page
│   ├── add_lot.html      # Add parking lot
│   ├── edit_lot.html     # Edit parking lot
│   ├── view_spot.html    # View spot details
│   ├── user_home.html    # User dashboard
│   ├── user_summary.html # User bookings
│   └── auth/
│       ├── login.html    # Login page
│       └── register.html # Registration page
│
└── static/
    └── css/
        └── style.css     # Custom CSS styles
```

## Key Technologies & Concepts

### Flask Framework
- Route management
- Template rendering with Jinja2
- Session management
- Flash messages for user feedback

### SQLAlchemy ORM
- Object-Relational Mapping
- Database relationships
- Query optimization
- Transaction management

### Security Features
- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection
- Login required decorators

### Bootstrap 5
- Responsive design
- Mobile-friendly interface
- Modern UI components
- Card-based layouts

## Non-Functional Requirements

- **Performance**: Response time < 2 seconds
- **Accuracy**: Real-time status updates
- **Security**: Secure password storage
- **Usability**: Clean, intuitive interface
- **Maintainability**: Modular, well-commented code

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Add comments for complex logic
- Use descriptive variable names
- Keep functions modular

### Database
- Always use db.session for transactions
- Commit changes after modifications
- Handle exceptions appropriately

### Templates
- Extend base templates for consistency
- Use Bootstrap classes for styling
- Implement responsive design
- Show appropriate feedback messages

## Testing Checklist

- [ ] User registration works
- [ ] User login/logout works
- [ ] Admin login works
- [ ] Add parking lot creates spots
- [ ] Edit lot modifies spots correctly
- [ ] Delete lot removes all spots
- [ ] Search by location works
- [ ] Book spot updates status
- [ ] Release spot frees the spot
- [ ] Booking history displays correctly
- [ ] Admin summary shows statistics
- [ ] User search finds users

## Common Issues & Solutions

### Issue: Database not created
**Solution**: Make sure the `instance` folder exists and has write permissions

### Issue: Cannot login
**Solution**: Check if user exists in database. For admin, create default admin first.

### Issue: Booking not working
**Solution**: Ensure spots are available (status='A') and user doesn't have active booking

### Issue: Spots not updating
**Solution**: Check database transactions are being committed properly

## Future Enhancements
- Payment gateway integration
- Email notifications
- Mobile app version
- QR code-based check-in
- Real-time availability map
- Booking history export
- User profile management
- Multiple admin roles

## Academic Information

**Institution**: Saveetha Engineering College  
**Project Type**: Mini Project - Review 1  
**Course**: Web Application Development  
**Year**: 2025

## Contributors

This project was developed as part of an academic curriculum.

## License

This project is developed for educational purposes.

## Support

For queries or issues, refer to the project documentation or contact your project guide.

---

**Note**: This project is designed for demonstration and academic evaluation. Ensure all functionality is tested before the viva presentation.
