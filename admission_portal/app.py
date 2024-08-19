from flask import Flask, render_template, redirect, request, url_for, flash, session
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Use absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
USER_DATA_FILE = os.path.join(BASE_DIR, 'database', 'user_data.xlsx')
ADMISSION_DATA_FILE = os.path.join(BASE_DIR, 'database', 'admission_data.xlsx')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'database', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def initialize_excel_files():
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(ADMISSION_DATA_FILE), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if not os.path.exists(USER_DATA_FILE):
        df = pd.DataFrame(columns=['Email', 'Username', 'Phone', 'Password'])
        df.to_excel(USER_DATA_FILE, index=False)

    if not os.path.exists(ADMISSION_DATA_FILE):
        df = pd.DataFrame(columns=[
            'Name', 'Contact', 'Father\'s Name', 'Mother\'s Name', 
            'Address', 'Fees Paid', 'Payment Date',
            'Total Amount', 'Balance Amount', 'Due Date',
            'Parent Contact', 'ID Proof', 'Marksheet'
        ])
        df.to_excel(ADMISSION_DATA_FILE, index=False)

initialize_excel_files()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        phone = request.form['phone']
        password = request.form['password']

        if len(phone) != 10 or not phone.isdigit():
            flash('Invalid phone number!')
            return redirect(url_for('create_account'))

        df = pd.read_excel(USER_DATA_FILE)
        new_row = pd.DataFrame({'Email': [email], 'Username': [username], 'Phone': [phone], 'Password': [password]})
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(USER_DATA_FILE, index=False)

        flash('Account created successfully!')
        return redirect(url_for('login'))

    return render_template('create_account.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']

        df = pd.read_excel(USER_DATA_FILE)
        user = df[(df['Email'] == username_or_email) | (df['Username'] == username_or_email)]
        if not user.empty and user.iloc[0]['Password'] == password:
            session['user'] = user.iloc[0]['Username']
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!')

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

        if len(contact) != 10 or not contact.isdigit():
            flash('Invalid contact number!')
            return redirect(url_for('submit_admission'))

        id_proof = request.files['id_proof']
        marksheet = request.files['marksheet']

        id_proof_filename = secure_filename(id_proof.filename)
        marksheet_filename = secure_filename(marksheet.filename)

        id_proof_path = os.path.join(app.config['UPLOAD_FOLDER'], id_proof_filename)
        marksheet_path = os.path.join(app.config['UPLOAD_FOLDER'], marksheet_filename)
        
        id_proof.save(id_proof_path)
        marksheet.save(marksheet_path)

        df = pd.read_excel(ADMISSION_DATA_FILE)
        new_row = pd.DataFrame({
            'Name': [name], 'Contact': [contact], 'Father\'s Name': [fathers_name],
            'Mother\'s Name': [mothers_name], 'Address': [address], 'Fees Paid': [fees_paid],
            'Payment Date': [payment_date], 'Total Amount': [total_amount],
            'Balance Amount': [balance_amount], 'Due Date': [due_date],
            'Parent Contact': [parent_contact], 'ID Proof': [id_proof_filename],
            'Marksheet': [marksheet_filename]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(ADMISSION_DATA_FILE, index=False)

        flash('Admission form submitted successfully!')
        return redirect(url_for('home'))
    
    return render_template('submit_admission.html')

if __name__ == '__main__':
    app.run(debug=True)