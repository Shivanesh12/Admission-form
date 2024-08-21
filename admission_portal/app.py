from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'admission_portal'
}

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        print("Successfully connected to MySQL database")
    except Error as e:
        print(f"Error: '{e}'")
    return connection

def init_db():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    phone VARCHAR(20),
                    password VARCHAR(255) NOT NULL
                )
            ''')

            connection.commit()
            print("Database initialized successfully")
        except Error as e:
            print(f"Error: '{e}'")
        finally:
            cursor.close()
            connection.close()

init_db
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        phone = request.form['phone']
        password = generate_password_hash(request.form['password'])
        
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (email, username, phone, password) VALUES (%s, %s, %s, %s)",
                               (email, username, phone, password))
                connection.commit()
                print(f"User created: {username}, {email}")
                return redirect(url_for('login'))
            except Error as e:
                print(f"Error: '{e}'")
                return "An error occurred while creating the account."
            finally:
                cursor.close()
                connection.close()

        
    return render_template('create_account.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, username))
                user = cursor.fetchone()

                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    print(f"Login successful for user: {username}")
                    return redirect(url_for('submit_admission'))
                else:
                    print(f"Invalid login attempt for user: {username}")
                    return "Invalid username or password"
            except Error as e :
                print(f"Error: '{e}'")
                return "An error occurred during login"
            finally:
                cursor.close()
                connection.close()

    return render_template('login.html')

@app.route('/submit_admission', methods=['GET', 'POST'])
def submit_admission():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        name = request.form['name']
        contact_number = request.form['contact_number']
        father_name = request.form['father_name']
        mother_name = request.form['mother_name']
        address = request.form['address']
        id_proof = request.files['id_proof'].filename
        marksheet = request.files['marksheet'].filename
        fees_paid = float(request.form['fees_paid'])
        payment_date = request.form['payment_date']
        total_amount = float(request.form['total_amount'])
        balance_amount = float(request.form['balance_amount'])
        due_date = request.form['due_date']
        parent_concat = request.form['parent_cotact']


        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT INTO admissions
                    (user_id, name, contact_number, father_name, mother_name, address,
                    id_proof, marksheet, fees_paid, payment_date, total_amount,
                    balance_amount, due_date, parent_contact)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (user_id, name, contact_number, father_name, mother_name, address,
                      id_proof, marksheet, fees_paid, payment_date, total_amount,
                      balance_amount, due_date, parent_concat))
                connection.commit()
                print(f"Admission submitted for user: {user_id}")
                return "Admission form submitted successfully"
            except Error as e:
                print(f"Error: '{e}'")
                return "An error occurred while submitting the admission form."
            finally:
                cursor.close()
                connection.close()

   
    return render_template('submit_admission.html')



if __name__ == '__main__':
    app.run(debug=True)