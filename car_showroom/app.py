from flask import Flask, request, redirect, url_for, session, render_template, flash
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration (update according to your settings in XAMPP)
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'car_showroom'
}

ADMIN_USERNAME = 'admin'  # Admin username for admin-only routes

# Index Route - Displays available vehicles
@app.route('/')
def index():
    search_query = request.args.get('search_query', '')
    sort_by = request.args.get('sort_by', 'year')
    order = request.args.get('order', 'ASC').upper()

    allowed_sort_columns = {'year', 'price', 'make', 'model'}
    allowed_order = {'ASC', 'DESC'}
    sort_by = sort_by if sort_by in allowed_sort_columns else 'year'
    order = order if order in allowed_order else 'ASC'

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch all vehicles or filter based on search query
        if search_query:
            query = f"SELECT * FROM Vehicle WHERE make LIKE %s OR model LIKE %s ORDER BY {sort_by} {order}"
            cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        else:
            query = f"SELECT * FROM Vehicle ORDER BY {sort_by} {order}"
            cursor.execute(query)

        vehicles = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('index.html', vehicles=vehicles, search_query=search_query, sort_by=sort_by, order=order)

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return render_template('error.html')


# Decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in session and session['username'] == ADMIN_USERNAME:
            return f(*args, **kwargs)
        else:
            flash("Admin access only!", 'danger')
            return redirect(url_for('index'))
    return wrap


# Login Route - Validates user credentials
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM User WHERE user_name = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                session['username'] = user['user_name']
                session['role'] = user['user_type']  # Store the role in the session
                flash("Logged in successfully!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid credentials!", "danger")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')

    return render_template('login.html')


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('index'))


# Signup Route - Creates a new user
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['ph_number']  # Assuming this field is in the form

        password_hash = generate_password_hash(password)
        role = 'user'  # Default role for new users
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO User (user_name, email, ph_number, user_type, password) VALUES (%s, %s, %s, %s, %s)", 
                           (username, email, phone_number, role,password_hash))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Account created successfully!", "success")
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')

    return render_template('signup.html')


# Add Vehicle Route (Admin Only) - Adds a new vehicle to the database
@app.route('/add_vehicle', methods=['GET', 'POST'])
@admin_required
def add_vehicle():
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        price = request.form['price']
        description = request.form['description']
        vehicle_type = request.form['vehicle_type']  # Assuming you are choosing between Car or Bike

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = "INSERT INTO Vehicle (make, model, year, price, description, vehcile_type) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (make, model, year, price, description, vehicle_type))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Vehicle added successfully!', 'success')
            return redirect(url_for('index'))

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')
    
    return render_template('add_vehicle.html')


# Add to Wishlist Route - Adds a vehicle to the user's wishlist
@app.route('/add_to_wishlist/<int:vehicle_id>')
def add_to_wishlist(vehicle_id):
    if 'user_id' not in session:
        flash("Please log in to add vehicles to your wishlist.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if vehicle is already in wishlist
        cursor.execute("SELECT * FROM Wishlist WHERE user_id = %s AND vehicle_id = %s", (user_id, vehicle_id))
        wishlist_item = cursor.fetchone()
        
        if wishlist_item:
            flash("Vehicle is already in your wishlist!", "info")
        else:
            cursor.execute("INSERT INTO Wishlist (user_id, vehicle_id) VALUES (%s, %s)", (user_id, vehicle_id))
            conn.commit()
            flash("Vehicle added to wishlist!", "success")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')

    return redirect(url_for('index'))


# Wishlist Route - Displays the user's wishlist
@app.route('/wishlist')
def wishlist():
    if 'user_id' not in session:
        flash("Please log in to view your wishlist.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Vehicle.* FROM Vehicle INNER JOIN Wishlist ON Vehicle.vehicle_id = Wishlist.vehicle_id WHERE Wishlist.user_id = %s", 
                       (user_id,))
        wishlist_vehicles = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('wishlist.html', vehicles=wishlist_vehicles)
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return render_template('error.html')


# Vehicle Details Route - Shows details of a specific vehicle
@app.route('/vehicle/<int:vehicle_id>')
def vehicle_details(vehicle_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch details for the specific vehicle by vehicle_id
        cursor.execute("SELECT * FROM Vehicle WHERE vehicle_id = %s", (vehicle_id,))
        vehicle = cursor.fetchone()
        cursor.close()
        conn.close()

        if vehicle:
            return render_template('vehicle_details.html', vehicle=vehicle)
        else:
            flash("Vehicle not found.", "danger")
            return redirect(url_for('index'))

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
        return redirect(url_for('index'))


# Schedule Test Drive Route
@app.route('/schedule_test_drive/<int:vehicle_id>', methods=['POST'])
def schedule_test_drive(vehicle_id):
    if 'user_id' not in session:
        flash("Please log in to schedule a test drive.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    # Assuming you want to capture date and time from the user (you may want to create a form for this)
    test_drive_date = request.form.get('test_drive_date')  # Capture date from the form
    test_drive_time = request.form.get('test_drive_time')    # Capture time from the form

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO TestDrive (user_id, vehicle_id, test_drive_date, test_drive_time) VALUES (%s, %s, %s, %s)", 
                       (user_id, vehicle_id, test_drive_date, test_drive_time))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Test drive scheduled successfully!", "success")
        return redirect(url_for('index'))
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
        return redirect(url_for('index'))



# View Test Drives Route (Admin Only)
@app.route('/view_test_drives')
@admin_required
def view_test_drives():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch all scheduled test drives
        cursor.execute("""
            SELECT User.user_name, Vehicle.make AS vehicle_make, Vehicle.model AS vehicle_model, 
                   TestDrive.test_drive_date, testDrive.test_drive_time
            FROM TestDrive
            JOIN User ON TestDrive.user_id = User.user_id
            JOIN Vehicle ON TestDrive.vehicle_id = Vehicle.vehicle_id
        """)
        test_drives = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('view_test_drives.html', test_drives=test_drives, current_year='2024')
    
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
