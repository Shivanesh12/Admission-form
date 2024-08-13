from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
EXCEL_FILE = 'admission_data.xlsx'

if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        'Name', 'Contact Number', 'Father\'s Name', 'Mother\'s Name', 'Address',
        'ID Proof', 'Marksheet', 'Fees Paid', 'Payment Date', 'Total Amount',
        'Balance Amount', 'Due Date', 'Parent\'s Contact Number'
    ])
    df.to_excel(EXCEL_FILE, index=False)

@app.route('/')
def index():
    return redirect(url_for('create_account'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('create_account'))

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('create_account.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'password':  # Replace with your logic
            flash('Login successful!', 'success')
            return redirect(url_for('submit_admission'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/submit_admission', methods=['GET', 'POST'])
def submit_admission():
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

    df = pd.read_excel(EXCEL_FILE)

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
    df.to_excel(EXCEL_FILE, index=False)

    flash('Admission form submitted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

