from flask import Flask, request, redirect, url_for, session, render_template, flash
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
import os


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

        # Fetch all vehicles or filter based on search query, including image
        if search_query:
            query = """
            SELECT Vehicle.*, Car.image 
            FROM Vehicle 
            JOIN Car ON Vehicle.vehicle_id = Car.vehicle_id 
            WHERE Vehicle.make LIKE %s OR Vehicle.model LIKE %s 
            ORDER BY {} {}
            """.format(sort_by, order)
            cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        else:
            query = """
            SELECT Vehicle.*, Car.image 
            FROM Vehicle 
            JOIN Car ON Vehicle.vehicle_id = Car.vehicle_id 
            ORDER BY {} {}
            """.format(sort_by, order)
            cursor.execute(query)

        vehicles = cursor.fetchall()
        print(vehicles)
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


UPLOAD_FOLDER = 'static/img'  # Change this to your desired path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Add Vehicle Route (Admin Only) - Adds a new vehicle to the database
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_vehicle', methods=['GET', 'POST'])
@admin_required
def add_vehicle():
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        price = request.form['price']
        description = request.form['description']
        vehicle_type = request.form['vehicle_type']

        # Handle the image upload
        if 'image' not in request.files:
            flash('No image part', 'danger')
            return redirect(request.url)
        image = request.files['image']
        
        if image.filename == '':
            flash('No selected image', 'danger')
            return redirect(request.url)
        
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            try:
                # Connect to the database
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()

                # Insert the vehicle into the Vehicle table
                query = "INSERT INTO Vehicle (make, model, year, price, description, vehicle_type) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (make, model, year, price, description, vehicle_type))
                vehicle_id = cursor.lastrowid  # Get the generated vehicle ID
                conn.commit()  # Commit the transaction for the Vehicle insert

                # Insert the image into the Cars table
                query = "INSERT INTO Car (vehicle_id, image) VALUES (%s, %s)"
                cursor.execute(query, (vehicle_id, filename))  # Use the vehicle_id obtained
                conn.commit()  # Commit the transaction for the Cars insert

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
        
        return render_template('wishlist.html', wishlist=wishlist_vehicles)  # Pass wishlist_vehicles as wishlist
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return render_template('error.html')


@app.route('/remove_from_wishlist/<int:vehicle_id>')
def remove_from_wishlist(vehicle_id):
    if 'user_id' not in session:
        flash("Please log in to manage your wishlist.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Wishlist WHERE user_id = %s AND vehicle_id = %s", 
                       (user_id, vehicle_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Vehicle removed from your wishlist.", "success")
        return redirect(url_for('wishlist'))
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return redirect(url_for('wishlist'))


# Vehicle Details Route - Shows details of a specific vehicle
@app.route('/vehicle/<int:vehicle_id>')
def vehicle_details(vehicle_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch details for the specific vehicle along with the image from the Car table
        cursor.execute("""
            SELECT v.*, c.image 
            FROM Vehicle v 
            JOIN Car c ON v.vehicle_id = c.vehicle_id 
            WHERE v.vehicle_id = %s
        """, (vehicle_id,))
        
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


@app.route('/inquiry/<int:vehicle_id>/<vehicle_make>/<vehicle_model>')
def inquiry(vehicle_id, vehicle_make, vehicle_model):
    # Process the vehicle_id, vehicle_make, and vehicle_model if needed
    return render_template('inquiry.html', vehicle_id=vehicle_id, vehicle_make=vehicle_make, vehicle_model=vehicle_model)


@app.route('/submit_inquiry/<int:vehicle_id>', methods=['POST'])
def submit_inquiry(vehicle_id):
    if 'user_id' not in session:
        flash("Please log in to make an inquiry.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    inquiry_text = request.form['inquiry_text']
    inquiry_date = datetime.now()

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert the inquiry into the database
        cursor.execute("""
            INSERT INTO inquiry (vehicle_id, user_id, inquiry_text, inquiry_date)
            VALUES (%s, %s, %s, %s)
        """, (vehicle_id, user_id, inquiry_text, inquiry_date))

        conn.commit()
        flash('Your inquiry has been submitted successfully!', 'success')
    
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
    
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('vehicle_details', vehicle_id=vehicle_id))  # Redirect back to vehicle details


@app.route('/view_inquiries')
@admin_required  # Ensure that only admin users can access this route
def view_inquiries():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch all inquiries from the inquiry table
        query = "SELECT * FROM inquiry"  # Adjust the table name as per your schema
        cursor.execute(query)
        inquiries = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('inquiry_view.html', inquiries=inquiries)

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return render_template('error.html')



if __name__ == '__main__':
    app.run(debug=True)
