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
# Index Route - Displays latest 8 vehicles
@app.route('/')
def index():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch the latest 8 vehicles, including their images
        query = """
        SELECT Vehicle.*, Car.image 
        FROM Vehicle 
        JOIN Car ON Vehicle.vehicle_id = Car.vehicle_id 
        ORDER BY Vehicle.vehicle_id DESC
        LIMIT 8
        """
        cursor.execute(query)
        vehicles = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('index.html', vehicles=vehicles)

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return render_template('error.html')


# Route to display all vehicles with search and filter options
@app.route('/show_all_cars')
def show_all_cars():
    # Get filter parameters from the request
    search_query = request.args.get('search_query', '')
    sort_by = request.args.get('sort_by', 'year')
    order = request.args.get('order', 'ASC').upper()
    vehicle_type = request.args.get('vehicle_type', '')

    # Define allowed values for filters
    allowed_sort_columns = {'year', 'price', 'make', 'model'}
    allowed_order = {'ASC', 'DESC'}
    allowed_types = {'suv', 'hatchback', 'sedan', 'sport', 'convertible', 'coupe', 
                     'bike', 'cruiser', 'touring', 'standard'}

    # Validate sort_by and order parameters
    sort_by = sort_by if sort_by in allowed_sort_columns else 'year'
    order = order if order in allowed_order else 'ASC'

    try:
        # Database connection
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Build dynamic query based on filters
        query = """
        SELECT Vehicle.*, Car.image 
        FROM Vehicle 
        JOIN Car ON Vehicle.vehicle_id = Car.vehicle_id
        WHERE 1=1
        """
        
        params = []

        # Apply search filter
        if search_query:
            query += " AND (Vehicle.make LIKE %s OR Vehicle.model LIKE %s)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        # Apply vehicle type filter
        if vehicle_type.lower() in allowed_types:
            # Add 'Car/' prefix to match database format
            query += " AND LOWER(vehicle_type) = %s"
            params.append(f"car/{vehicle_type.lower()}")

        # Sorting
        query += f" ORDER BY {sort_by} {order}"

        # Execute the query
        cursor.execute(query, tuple(params))
        vehicles = cursor.fetchall()

        # Close connections
        cursor.close()
        conn.close()

        # Render the template with filtered results
        return render_template(
            'show_all_cars.html',
            vehicles=vehicles,
            search_query=search_query,
            sort_by=sort_by,
            order=order,
            vehicle_type=vehicle_type
        )

    except mysql.connector.Error as err:
        # Handle database errors
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
        category = request.form['category']

        # Combine vehicle type and category for filtering purposes
        vehicle_type_with_category = f"{vehicle_type}/{category}"

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

                # Insert the vehicle into the Vehicle table with the combined vehicle_type
                query = "INSERT INTO Vehicle (make, model, year, price, description, vehicle_type) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (make, model, year, price, description, vehicle_type_with_category))
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

        # Fetch installment plans for the specific vehicle
        cursor.execute("""
            SELECT downpayment, monthly_installment, interest_rate, total_price, bank_name, time_period
            FROM installment
            WHERE vehicle_id = %s
        """, (vehicle_id,))
        
        installments = cursor.fetchall()

        cursor.close()
        conn.close()

        if vehicle:
            # Pass both vehicle details and installment plans to the template
            return render_template('vehicle_details.html', vehicle=vehicle, installments=installments)
        else:
            flash("Vehicle not found.", "danger")
            return redirect(url_for('index'))

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
        return redirect(url_for('index'))


# Route to delete a vehicle (Admin only)
@app.route('/delete_vehicle/<int:vehicle_id>', methods=['GET'])
def delete_vehicle(vehicle_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Delete the vehicle from the Car table (or related table if necessary)
        cursor.execute("DELETE FROM Vehicle WHERE vehicle_id = %s", (vehicle_id,))
        cursor.execute("DELETE FROM Car WHERE vehicle_id = %s", (vehicle_id,))

        conn.commit()

        cursor.close()
        conn.close()

        flash("Vehicle deleted successfully.", "success")
        return redirect(url_for('index'))  # Redirect to homepage or vehicle list page

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


# Route to display the form and add an installment plan
@app.route('/add_installment/<int:vehicle_id>', methods=['GET', 'POST'])
def add_installment(vehicle_id):
    if request.method == 'POST':
        # Retrieve form data
        downpayment = request.form.get('downpayment')
        monthly_installment = request.form.get('monthly_installment')
        interest_rate = request.form.get('interest_rate')
        total_price = request.form.get('total_price')
        bank_name = request.form.get('bank_name')
        time_period = request.form.get('time_period')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Insert the installment details into the Installment table
            cursor.execute("""
                INSERT INTO Installment (vehicle_id, downpayment, monthly_installment, interest_rate, total_price, bank_name, time_period)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (vehicle_id, downpayment, monthly_installment, interest_rate, total_price, bank_name, time_period))
            
            conn.commit()
            cursor.close()
            conn.close()

            flash("Installment plan added successfully.", "success")
            return redirect(url_for('vehicle_details', vehicle_id=vehicle_id))

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
            return redirect(url_for('vehicle_details', vehicle_id=vehicle_id))

    return render_template('add_installment_plan.html', vehicle_id=vehicle_id)



@app.route('/view_test_drives', methods=['GET', 'POST'])
@admin_required
def view_test_drives():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            # Update the test drive status
            testdrive_id = request.form['testdrive_id']
            new_status = request.form['status']
            cursor.execute(
                "UPDATE TestDrive SET status = %s WHERE testdrive_id = %s",
                (new_status, testdrive_id)
            )
            conn.commit()
            flash('Test drive status updated successfully.', 'success')

        # Fetch all test drives
        cursor.execute("""
            SELECT TestDrive.testdrive_id, User.user_name, Vehicle.make AS vehicle_make, Vehicle.model AS vehicle_model, 
                   TestDrive.test_drive_date, TestDrive.test_drive_time, TestDrive.status
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


@app.route('/delete_test_drive/<int:testdrive_id>', methods=['POST'])
def delete_test_drive(testdrive_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM TestDrive WHERE testdrive_id = %s", (testdrive_id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash("Test drive deleted successfully.", "success")
        return redirect(url_for('view_test_drives'))
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return redirect(url_for('view_test_drives'))
    

@app.route('/my_test_drives')
def my_test_drives():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch test drives for the logged-in user
        user_id = session['user_id']
        cursor.execute("""
            SELECT TestDrive.testdrive_id, Vehicle.make AS vehicle_make, Vehicle.model AS vehicle_model, 
                   TestDrive.test_drive_date, TestDrive.test_drive_time, TestDrive.status
            FROM TestDrive
            JOIN Vehicle ON TestDrive.vehicle_id = Vehicle.vehicle_id
            WHERE TestDrive.user_id = %s
        """, (user_id,))
        user_test_drives = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('my_test_drives.html', test_drives=user_test_drives, current_year='2024')

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return redirect(url_for('index'))
   


# Inquiry Route - Displays the inquiry form
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
    

@app.route('/reply_inquiry/<int:inquiry_id>', methods=['POST'])
@admin_required
def reply_inquiry(inquiry_id):
    try:
        reply_text = request.form['reply']
        reply_date = datetime.now()


        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Update the inquiry with the admin's reply
        update_query = "UPDATE inquiry SET reply = %s, reply_date = %s WHERE inquiry_id = %s"
        cursor.execute(update_query, (reply_text, reply_date, inquiry_id))
        conn.commit()

        cursor.close()
        conn.close()

        flash("Reply sent successfully!", 'success')
        return redirect(url_for('view_inquiries'))

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return redirect(url_for('view_inquiries'))


@app.route('/my_inquiries')
def my_inquiries():
    if 'username' in session:
        user_id = session['user_id']
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # Fetch the user's inquiries
            query = "SELECT * FROM inquiry WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            inquiries = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template('my_inquiries.html', inquiries=inquiries)

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')
            return render_template('error.html')



@app.route('/delete_inquiry/<int:inquiry_id>', methods=['POST'])
@admin_required  # Ensure that only admin users can access this route
def delete_inquiry(inquiry_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Delete the inquiry from the database
        cursor.execute("DELETE FROM inquiry WHERE inquiry_id = %s", (inquiry_id,))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Inquiry deleted successfully.', 'success')
        return redirect(url_for('view_inquiries'))

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return redirect(url_for('view_inquiries'))



if __name__ == '__main__':
    app.run(debug=True)
