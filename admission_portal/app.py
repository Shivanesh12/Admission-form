from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


def init_db():
    conn = sqlite3.connect('admission_portal.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, email TEXT, username TEXT, phone TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admissions
                 (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, contact_number TEXT, 
                 father_name TEXT, mother_name TEXT, address TEXT, id_proof TEXT, 
                 marksheet TEXT, fees_paid REAL, payment_date TEXT, total_amount REAL, 
                 balance_amount REAL, due_date TEXT, parent_contact TEXT)''')
    conn.commit()
    conn.close()

init_db()


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
        
        try:
            conn = sqlite3.connect('admission_portal.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (email, username, phone, password) VALUES (?, ?, ?, ?)",
                     (email, username, phone, password))
            conn.commit()
            print(f"User created: {username}, {email}")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return "An error occurred while creating the account."
        finally:
            conn.close()
        
        return redirect(url_for('login'))
    return render_template('create_account.html')

@app.route('/check_users')
def check_users():
    try:
        conn = sqlite3.connect('admission_portal.db')
        c = conn.cursor()
        c.execute("SELECT id, email, username, phone FROM users")
        users = c.fetchall()
        conn.close()
        return f"Users in database: {users}"
    except sqlite3.Error as e :
        return f"An error occured: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = sqlite3.connect('admission_portal.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username))
            user = c.fetchone()
            conn.close()
        
            if user:
                if check_password_hash(user[4], password):
                    session['user_id'] = user[0]
                    print(f"User {user[0]} logged in successfully")
                    return redirect(url_for('submit_admission'))
                else:
                    print(f"Invalid password for user {username}")
                    return "Invalid username or password"
            else:
                print(f"Invalid password for user {username}")
                return "Invalid username or password"
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return "An error occured during login"
    return render_template('login.html')

@app.route('/submit_admission', methods=['GET', 'POST'])
def submit_admission():

    print(f"Current session: {session}")
    if 'user_id' not in session:
        print("User not in session, redirecting to login")
        return redirect(url_for('login'))
    
    print(f"User {session['user_id']} accessing submit_admission")

    if request.method == 'POST':
        # Extract form data
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
        parent_contact = request.form['parent_contact']
        
        # Save files
        request.files['id_proof'].save(os.path.join('uploads', id_proof))
        request.files['marksheet'].save(os.path.join('uploads', marksheet))
        
        # Insert data into database
        conn = sqlite3.connect('admission_portal.db')
        c = conn.cursor()
        c.execute('''INSERT INTO admissions 
                     (user_id, name, contact_number, father_name, mother_name, address, 
                     id_proof, marksheet, fees_paid, payment_date, total_amount, 
                     balance_amount, due_date, parent_contact) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], name, contact_number, father_name, mother_name, 
                   address, id_proof, marksheet, fees_paid, payment_date, total_amount, 
                   balance_amount, due_date, parent_contact))
        conn.commit()
        conn.close()
        
        return "Admission form submitted successfully"
    return render_template('submit_admission.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


import pandas as pd

def export_users_to_excel():
    conn = sqlite3.connect('admission_portal.db')
    users_df = pd.read_sql_query("SELECT * FROM users", conn)
    users_df.to_excel('user_data.xlsx', index=False)
    conn.close()

def export_admissions_to_excel():
    conn = sqlite3.connect('admission_portal.db')
    admissions_df = pd.read_sql_query("SELECT * FROM admissions", conn)
    admissions_df.to_excel('admission_data.xlsx', index=False)
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)