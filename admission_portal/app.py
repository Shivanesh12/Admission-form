
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
import os
import pandas as pd


app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

# Excel file paths
USER_EXCEL_FILE = 'data/user_data.xlsx'
ADMISSION_EXCEL_FILE = 'data/admission_data.xlsx'

# Initialize the user Excel file if it doesn't exist
if not os.path.exists(USER_EXCEL_FILE):
    df = pd.DataFrame(columns=['Email', 'Username', 'Phone', 'Password'])
    df.to_excel(USER_EXCEL_FILE, index=False)

# Initialize the admission Excel file if it doesn't exist
if not os.path.exists(ADMISSION_EXCEL_FILE):
    df = pd.DataFrame(columns=[
        'Name', 'Contact Number', 'Father\'s Name', 'Mother\'s Name', 'Address',
        'ID Proof', 'Marksheet', 'Fees Paid', 'Payment Date', 'Total Amount',
        'Balance Amount', 'Due Date', 'Parent\'s Contact Number'
    ])
    df.to_excel(ADMISSION_EXCEL_FILE, index=False)

@app.route('/')
def index():
    return redirect(url_for('create_account'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        phone = request.form['phone']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']

        if password != confirmpassword:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('create_account'))

        # Load the current user data
        if os.path.exists(USER_EXCEL_FILE):
            df = pd.read_excel(USER_EXCEL_FILE)
        else:
            df = pd.DataFrame(columns=['Email', 'Username', 'Phone',  'Password'])

        # Check if username already exists
        if not df[df['Username'] == username].empty:
            flash('Username already exists!', 'danger')
            return redirect(url_for('create_account'))
        
        # Hash the password
        hashed_password = generate_password_hash(password, method='sha256')

        # Append new user data
        new_user = pd.DataFrame({'Email': [email], 'Username': [username], 'Phone': [phone], 'Password':[hashed_password]})
    
        df = pd.concat([df, new_user], ignore_index=True)
        df.to_excel(USER_EXCEL_FILE, index=False)

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('create_account.html')



@app.route('/login', methods=['GET', 'POST'])        
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Load the user data
        df = pd.read_excel(USER_EXCEL_FILE)

        # Check for matching credentials
        user = df[(df['Username'] == username) & (df['Password'] == password)]

        if not user.empty:
            flash('Login successful!', 'success')
            return redirect(url_for('submit_admission'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/submit_admission', methods=['GET', 'POST'])
def submit_admission():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        fathers_name = request.form['fathers_name']
        mothers_name = request.form['mothers_name']
        address = request.form['address']
        fees_paid = request.form['fees_paid']
        payment_date = request.form['payment_date']
        total_amount = request.form['total_amount']
        balance_amount = request.form['balance_amount']
        due_date = request.form['due_date']
        parent_contact = request.form['parent_contact']

        id_proof = request.files['id_proof']
        marksheet = request.files['marksheet']

        id_proof_filename = os.path.join(UPLOAD_FOLDER, id_proof.filename)
        marksheet_filename = os.path.join(UPLOAD_FOLDER, marksheet.filename)
        id_proof.save(id_proof_filename)
        marksheet.save(marksheet_filename)

        df = pd.read_excel(ADMISSION_EXCEL_FILE)
        new_row = {
            'Name': name,
            'Contact Number': contact,
            'Father\'s Name': fathers_name,
            'Mother\'s Name': mothers_name,
            'Address': address,
            'ID Proof': id_proof_filename,
            'Marksheet': marksheet_filename,
            'Fees Paid': fees_paid,
            'Payment Date': payment_date,
            'Total Amount': total_amount,
            'Balance Amount': balance_amount,
            'Due Date': due_date,
            'Parent\'s Contact Number': parent_contact
        }
        df = df.append(new_row, ignore_index=True)
        df.to_excel(ADMISSION_EXCEL_FILE, index=False)

        flash('Admission form submitted successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('submit_admission.html')

if __name__ == '__main__':
    app.run(debug=True)