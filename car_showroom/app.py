from flask import Flask, request, redirect, url_for, session, render_template, flash
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy credentials for demonstration (In production, store securely in the database)
users = {
    "admin": generate_password_hash("admin123"),
    "user": generate_password_hash("user123")
}

ADMIN_USERNAME = "admin"

# MySQL configuration (update according to your settings in XAMPP)
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'car_showroom'
}

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

        # Fetch all cars if search_query is empty; otherwise, apply search filter
        if search_query:
            query = f"SELECT * FROM cars WHERE make LIKE %s OR model LIKE %s ORDER BY {sort_by} {order}"
            cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        else:
            query = f"SELECT * FROM cars ORDER BY {sort_by} {order}"
            cursor.execute(query)

        cars = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('index.html', cars=cars, search_query=search_query, sort_by=sort_by, order=order)

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


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         if username in users and check_password_hash(users[username], password):
#             session['username'] = username
#             flash('Login successful!', 'success')
#             return redirect(url_for('index'))
#         else:
#             flash('Invalid credentials!', 'danger')
    
#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']  # Store the role in the session
                flash("Logged in successfully!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid credentials!", "danger")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        password_hash = generate_password_hash(password)
        role = 'user'  # Automatically assign the 'user' role for new registrations
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)", 
                           (username, email, password_hash, role))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Account created successfully!", "success")
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')

    return render_template('signup.html')



@app.route('/add_car', methods=['GET', 'POST'])
@admin_required
def add_car():
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        price = request.form['price']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = "INSERT INTO cars (make, model, year, price) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (make, model, year, price))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Car added successfully!', 'success')
            return redirect(url_for('index'))

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')
    
    return render_template('add_car.html')


@app.route('/add_to_wishlist/<int:car_id>')
def add_to_wishlist(car_id):
    if 'user_id' not in session:
        flash("Please log in to add cars to your wishlist.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if car is already in wishlist
        cursor.execute("SELECT * FROM wishlists WHERE user_id = %s AND car_id = %s", (user_id, car_id))
        wishlist_item = cursor.fetchone()
        
        if wishlist_item:
            flash("Car is already in your wishlist!", "info")
        else:
            cursor.execute("INSERT INTO wishlists (user_id, car_id) VALUES (%s, %s)", (user_id, car_id))
            conn.commit()
            flash("Car added to wishlist!", "success")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')

    return redirect(url_for('index'))


@app.route('/wishlist')
def wishlist():
    if 'user_id' not in session:
        flash("Please log in to view your wishlist.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT cars.* FROM cars INNER JOIN wishlists ON cars.id = wishlists.car_id WHERE wishlists.user_id = %s", 
                       (user_id,))
        wishlist_cars = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('wishlist.html', cars=wishlist_cars)
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)
