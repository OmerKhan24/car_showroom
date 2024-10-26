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
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM cars"
        cursor.execute(query)
        cars = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', cars=cars, search_query='', sort_by='year', order='ASC')

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/search_cars', methods=['GET'])
def search_cars():
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

        query = f"SELECT * FROM cars WHERE make LIKE %s OR model LIKE %s ORDER BY {sort_by} {order}"
        cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        cars = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', cars=cars, search_query=search_query, sort_by=sort_by, order=order)

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return render_template('error.html')


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

if __name__ == '__main__':
    app.run(debug=True)
