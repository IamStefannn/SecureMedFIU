from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
import sqlite3, hashlib, os, random, string
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET", os.urandom(24).hex())

DB_PATH = "securemed.db"
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "qIkBRr-hIef_oyohOmekF3N_lvAmNmo0xceLQqDO-AQ=")
cipher = Fernet(ENCRYPTION_KEY.encode())


# helpers n stuff
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def normalize_dob(dob):
    # just make the date normal with leading zeros
    # accepts like 1/1/2000 or 2000-1-1 whatever
    try:
        for fmt in ["%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%Y/%m/%d"]:
            try:
                date_obj = datetime.strptime(dob, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return dob
    except:
        return dob


def validate_password_complexity(password):
    # check if password good enough
    # need 8 chars, upper, lower, number, special char
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    special_chars = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character (!@#$%^&*etc.)"

    # block dumb passwords people always use
    common_passwords = ["Password123!", "Admin123!", "Nurse123!", "12345678!", "Welcome123!"]
    if password in common_passwords:
        return False, "This password is too common. Please choose a more unique password"

    return True, "Password is valid"


def log_activity(username, action_type, description, details=None):
    # save what user did to audit log
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        ip_address = request.remote_addr if request else 'N/A'
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""INSERT INTO activity_log (timestamp, username, action_type, description, details, ip_address)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (timestamp, username, action_type, description, details, ip_address))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging activity: {e}")


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "role" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapper


def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("user_dashboard"))
        return f(*args, **kwargs)
    return wrapper


def nurse_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "user":
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return wrapper


def generate_mrn():
    # make random mrn that aint used yet
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    while True:
        mrn = f"MRN{random.randint(1000, 9999)}"
        c.execute("SELECT id FROM patients WHERE mrn=?", (mrn,))
        if not c.fetchone():
            conn.close()
            return mrn


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # users table - has security stuff n compliance scores
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE, password TEXT, role TEXT,
        dob TEXT, ssn_last4 TEXT,
        compliance_score INTEGER DEFAULT 0,
        training_completed INTEGER DEFAULT 0,
        last_training_date TEXT,
        completed_modules TEXT DEFAULT '[]')""")

    # patients table - all the patient info
    c.execute("""CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mrn TEXT UNIQUE, first_name TEXT, last_name TEXT,
        date_of_birth TEXT, email TEXT, phone TEXT, address TEXT,
        ssn TEXT, created_at TEXT, created_by TEXT)""")

    # audit results - violations n stuff
    c.execute("""CREATE TABLE IF NOT EXISTS audit_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT, severity TEXT, timestamp TEXT,
        details TEXT, recommendation TEXT, hipaa_section TEXT,
        source TEXT DEFAULT 'scanner', status TEXT DEFAULT 'Unresolved',
        nurse_username TEXT,
        acknowledged_at TEXT,
        acknowledged_by TEXT,
        remediation_deadline TEXT)""")

    # assignments - tasks for nurses
    c.execute("""CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type TEXT, patient_mrn TEXT, target_value TEXT,
        description TEXT, assigned_by TEXT, assigned_to TEXT,
        status TEXT DEFAULT 'Pending', created_at TEXT,
        completed_at TEXT, hipaa_section TEXT)""")

    # directory - approved places to send stuff
    c.execute("""CREATE TABLE IF NOT EXISTS directory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT, name TEXT, value TEXT, department TEXT, notes TEXT)""")

    # activity log - tracks everything
    c.execute("""CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        username TEXT NOT NULL,
        action_type TEXT NOT NULL,
        description TEXT NOT NULL,
        details TEXT,
        ip_address TEXT)""")

    # add address column if its missing
    try:
        c.execute("ALTER TABLE patients ADD COLUMN address TEXT")
        print("✅ Added address column to patients table")
    except sqlite3.OperationalError:
        pass

    # Default accounts with security info - Team Members
    if not c.execute("SELECT * FROM users").fetchone():
        c.executemany("INSERT INTO users (username,password,role,dob,ssn_last4) VALUES (?,?,?,?,?)", [
            ("admin", hash_pw("Admin123!"), "admin", "1985-06-15", "1234"),
            ("stefan", hash_pw("Stefan123!"), "user", "2001-10-19", "7294"),
            ("ana", hash_pw("Ana123!"), "user", "2005-03-12", "8163"),
            ("jordan", hash_pw("Jordan123!"), "user", "2002-11-27", "5947"),
            ("jeremiah", hash_pw("Jeremiah123!"), "user", "2003-05-17", "3821"),
            ("mumin", hash_pw("Mumin123!"), "user", "2003-02-15", "6502")
        ])
        print("âœ… Created default users with security info")
    
    # Sample patients - removed automatic generation
    # Use "Quick Setup" or /api/seed_patients to generate demo patients
    # Directory entries - 25 realistic entries (5 per category)
    if c.execute("SELECT COUNT(*) FROM directory").fetchone()[0] == 0:
        directory_entries = [
            # Fax Approved (5 entries)
            ('Fax Approved', 'St. Mary\'s Hospital - Radiology', '(555) 723-4400', 'Radiology', '1200 Medical Center Dr, Building A, Floor 2'),
            ('Fax Approved', 'City General - Cardiology Dept', '(555) 892-1155', 'Cardiology', '450 Healthcare Plaza, Suite 300, Springfield, IL 62701'),
            ('Fax Approved', 'SecureMed Billing Department', '(555) 234-2000', 'Billing', 'Internal - 789 Admin Blvd, Room 105'),
            ('Fax Approved', 'Valley Orthopedics Center', '(555) 456-7890', 'Orthopedics', '890 Medical Park Way, Building 3, Springfield, IL 62703'),
            ('Fax Approved', 'Regional Laboratory Services', '(555) 334-8899', 'Laboratory', '220 Science Blvd, Floor 1, Springfield, IL 62705'),
            # Email Secure (5 entries)
            ('Email Secure', 'Medical Records Department', 'records@securemed.internal', 'Records', 'Use encrypted email only - Internal system'),
            ('Email Secure', 'Insurance Pre-Authorization', 'preauth@securemed.internal', 'Insurance', 'For insurance claims and pre-auth requests'),
            ('Email Secure', 'Lab Results Coordination', 'labresults@securemed.internal', 'Laboratory', 'Secure portal for lab result transmission'),
            ('Email Secure', 'Specialist Referrals', 'referrals@securemed.internal', 'Care Coordination', 'For specialist consultation requests'),
            ('Email Secure', 'Imaging Department', 'imaging@securemed.internal', 'Radiology', 'CT, MRI, and X-ray report distribution'),
            # Hospital Transfer (5 entries)
            ('Hospital Transfer', 'St. Mary\'s Hospital - Emergency', '2500 Medical Center Dr, Springfield, IL 62702', 'Emergency', 'ER Receiving - Use secure transfer line (555) 723-4911'),
            ('Hospital Transfer', 'Regional Medical Center - ICU', '3400 Healthcare Pkwy, Building C, Floor 4, Springfield, IL 62704', 'Critical Care', 'Contact Charge Nurse at (555) 445-7800 before transfer'),
            ('Hospital Transfer', 'Downtown Specialty Clinic', '125 Main Street, Suite 200, Springfield, IL 62701', 'Specialists', 'Referrals for Cardiology, Neurology, Oncology'),
            ('Hospital Transfer', 'Memorial Hospital - Surgical Unit', '5600 University Ave, Springfield, IL 62706', 'Surgery', 'Pre-surgical admissions - Call (555) 667-3200 ext. 401'),
            ('Hospital Transfer', 'Springfield Rehabilitation Center', '1880 Wellness Drive, Springfield, IL 62708', 'Rehabilitation', 'Physical therapy and post-acute care'),
            # Courier Service (5 entries)
            ('Courier Service', 'MedCourier Express', 'Pickup: Building C Main Entrance, 789 Admin Blvd', 'Logistics', 'Scheduled pickups M-F 10am, 2pm, 5pm - Call (555) 768-2100'),
            ('Courier Service', 'SecureTransport Medical', 'Drop-off: Loading Dock B, Rear of Building A', 'Logistics', 'HIPAA-compliant transport - Tracking # required'),
            ('Courier Service', 'QuickMed Delivery Service', '450 Healthcare Plaza, Central Receiving', 'Logistics', 'Same-day delivery within 5 miles - (555) 892-3344'),
            ('Courier Service', 'Priority Health Logistics', '789 Admin Blvd, Suite 100', 'Logistics', 'Overnight delivery available - Temperature controlled'),
            ('Courier Service', 'CareLink Transport Services', 'Central Hub: 3200 Distribution Pkwy', 'Logistics', 'Multi-facility routing - Call (555) 445-9900 for scheduling'),
            # Secure Messaging (5 entries)
            ('Secure Messaging', 'Dr. Sarah Chen - Internal Medicine', 'SM-1847', 'Internal Medicine', 'Secure message via internal system - Patient consults'),
            ('Secure Messaging', 'Pharmacy - Prescription Refills', 'RX-4402', 'Pharmacy', 'Use for prescription renewals and clarifications'),
            ('Secure Messaging', 'Care Coordination Team', 'MSG-7733', 'Care Management', 'Discharge planning and follow-up coordination'),
            ('Secure Messaging', 'Dr. Michael Roberts - Cardiology', 'CARD-8821', 'Cardiology', 'Cardiac consultation and follow-up'),
            ('Secure Messaging', 'Nurse Practitioner - Primary Care', 'NP-5544', 'Primary Care', 'Routine follow-ups and medication management')
        ]
        c.executemany("INSERT INTO directory (type,name,value,department,notes) VALUES (?,?,?,?,?)", directory_entries)
        print("✅ Added 25 directory entries (5 per category)")

    conn.commit()
    conn.close()


init_db()


# ---------------------------- Auth ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form["username"].strip().lower()  # Case-insensitive username
        password = hash_pw(request.form["password"])
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username, role FROM users WHERE LOWER(username)=? AND password=?", (username, password))
        row = c.fetchone()
        conn.close()
        if not row:
            log_activity(username, "LOGIN_FAILED", f"Failed login attempt for user: {username}")
            return render_template("login.html", error="Invalid credentials")
        actual_username, role = row[0], row[1]
        session["role"], session["user"] = role, actual_username
        log_activity(actual_username, "LOGIN", f"User logged in as {role}")
        return redirect(url_for("dashboard" if role=="admin" else "user_dashboard"))
    return render_template("login.html")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"].strip().lower()  # Case-insensitive
        dob = normalize_dob(request.form["dob"].strip())  # Auto-format with leading zeros
        ssn_last4 = request.form["ssn_last4"].strip()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE LOWER(username)=? AND dob=? AND ssn_last4=?",
                 (username, dob, ssn_last4))
        user = c.fetchone()
        conn.close()

        if user:
            session["reset_user"] = username
            return redirect(url_for("reset_password"))
        else:
            return render_template("forgot_password.html", error="Verification failed. Please check your information.")

    return render_template("forgot_password.html")


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if "reset_user" not in session:
        return redirect(url_for("forgot_password"))
    
    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            return render_template("reset_password.html", error="Passwords do not match")

        # Validate password complexity
        is_valid, message = validate_password_complexity(new_password)
        if not is_valid:
            return render_template("reset_password.html", error=message)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET password=? WHERE username=?",
                 (hash_pw(new_password), session["reset_user"]))
        conn.commit()
        conn.close()

        # Log password reset to audit trail
        log_activity(session["reset_user"], "PASSWORD_RESET",
                    f"Password reset completed for user: {session['reset_user']}",
                    "Password changed via forgot password flow")

        session.pop("reset_user", None)
        return render_template("reset_password.html", success="Password reset successful! You can now login.")
    
    return render_template("reset_password.html")


@app.route("/logout")
def logout():
    username = session.get("user", "Unknown")
    log_activity(username, "LOGOUT", f"User {username} logged out")
    session.clear()
    return redirect(url_for("login_page"))


# ---------------------------- Dashboards ----------------------------
@app.route("/")
@login_required
def home_redirect():
    return redirect(url_for("dashboard" if session["role"]=="admin" else "user_dashboard"))


@app.route("/dashboard")
@admin_only
def dashboard():
    return render_template("dashboard_react.html")


@app.route("/user_dashboard")
@login_required
def user_dashboard():
    return render_template("user_dashboard_react.html", username=session.get("user", ""))


@app.route("/my_violations")
@nurse_only
def my_violations_page():
    return render_template("my_violations.html")


@app.route("/edr")
@login_required
def edr():
    return render_template("edr.html")


@app.route("/directory")
@login_required
def directory():
    return render_template("directory.html")


# ---------------------------- Patients API ----------------------------
@app.route("/api/patients", methods=["GET"])
@login_required
def get_patients():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, mrn, first_name, last_name, date_of_birth, email, phone, address, created_at, created_by FROM patients")
    rows = c.fetchall()
    conn.close()

    patients = []
    for row in rows:
        patients.append({
            "id": row[0], "mrn": row[1], "first_name": row[2], "last_name": row[3],
            "date_of_birth": row[4], "email": row[5], "phone": row[6], "address": row[7],
            "created_at": row[8], "created_by": row[9]
        })
    return jsonify(patients)


@app.route("/api/patients/add", methods=["POST"])
@login_required
def add_patient():
    data = request.json
    mrn = generate_mrn()
    enc_ssn = cipher.encrypt(data.get("ssn", "000-00-0000").encode()).decode()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO patients (mrn, first_name, last_name, date_of_birth, email, phone, address, ssn, created_by, created_at)
                 VALUES (?,?,?,?,?,?,?,?,?,?)""",
             (mrn, data["first_name"], data["last_name"], data["date_of_birth"],
              data.get("email",""), data.get("phone",""), data.get("address",""), enc_ssn, session["user"],
              datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

    # Log activity
    patient_name = f"{data['first_name']} {data['last_name']}"
    log_activity(session["user"], "PATIENT_ADDED", f"Added new patient: {patient_name}", f"MRN: {mrn}")

    return jsonify({"message": "Patient added", "mrn": mrn})


@app.route("/api/patients/<int:pid>", methods=["DELETE"])
@admin_only
def delete_patient(pid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM patients WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Patient deleted"})


@app.route("/api/patients/<int:pid>/view", methods=["GET"])
@login_required
def view_patient(pid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT mrn, first_name, last_name, date_of_birth, email, phone, address, ssn FROM patients WHERE id=?", (pid,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Patient not found"}), 404

    try:
        dec_ssn = cipher.decrypt(row[7].encode()).decode()
    except:
        dec_ssn = "***DECRYPTION ERROR***"

    return jsonify({
        "mrn": row[0], "first_name": row[1], "last_name": row[2],
        "date_of_birth": row[3], "email": row[4], "phone": row[5], "address": row[6], "ssn": dec_ssn
    })


@app.route("/api/patients/<int:pid>/update", methods=["PUT"])
@login_required
def update_patient(pid):
    """Update patient information (address, phone, email only - editable fields)"""
    data = request.json

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get current patient data
    c.execute("SELECT mrn, first_name, last_name, email, phone, address FROM patients WHERE id=?", (pid,))
    current = c.fetchone()

    if not current:
        conn.close()
        return jsonify({"error": "Patient not found"}), 404

    # Extract editable fields from request
    new_email = data.get("email", current[3])
    new_phone = data.get("phone", current[4])
    new_address = data.get("address", current[5])

    # Update only editable fields
    c.execute("""UPDATE patients SET email=?, phone=?, address=? WHERE id=?""",
             (new_email, new_phone, new_address, pid))

    # Log the update to audit trail
    changes = []
    if new_email != current[3]:
        changes.append(f"email: '{current[3]}' → '{new_email}'")
    if new_phone != current[4]:
        changes.append(f"phone: '{current[4]}' → '{new_phone}'")
    if new_address != current[5]:
        changes.append(f"address: '{current[5]}' → '{new_address}'")

    if changes:
        change_summary = ", ".join(changes)
        log_activity(session['user'], "PATIENT_INFO_UPDATED",
                    f"Updated patient {current[0]} ({current[1]} {current[2]})",
                    f"Changes: {change_summary}")

    conn.commit()
    conn.close()

    return jsonify({"message": "Patient information updated successfully"})


# ---------------------------- Assignments API ----------------------------
@app.route("/api/assignments", methods=["GET"])
@login_required
def get_assignments():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if session["role"] == "admin":
        c.execute("SELECT * FROM assignments ORDER BY created_at DESC")
    else:
        c.execute("SELECT * FROM assignments WHERE assigned_to=? ORDER BY created_at DESC", (session["user"],))
    
    rows = c.fetchall()
    conn.close()
    
    assignments = []
    for row in rows:
        assignments.append({
            "id": row[0], "task_type": row[1], "patient_mrn": row[2], "target_value": row[3],
            "description": row[4], "assigned_by": row[5], "assigned_to": row[6],
            "status": row[7], "created_at": row[8], "completed_at": row[9],
            "hipaa_section": row[10]
        })
    return jsonify(assignments)


@app.route("/api/assignments/generate", methods=["POST"])
@admin_only
def generate_assignments():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT mrn FROM patients ORDER BY RANDOM() LIMIT 3")
    patient_mrns = [r[0] for r in c.fetchall()]
    
    c.execute("SELECT username FROM users WHERE role='user'")
    nurses = [r[0] for r in c.fetchall()]
    
    if not nurses or not patient_mrns:
        conn.close()
        return jsonify({"error": "No nurses or patients available"}), 400
    
    c.execute("SELECT type, name, value FROM directory")
    directory_entries = c.fetchall()
    
    # Map task types to directory search keywords
    task_mapping = {
        "fax": ("Fax Approved", "Fax patient records to", "164.312(e)(1)"),
        "email": ("Email Secure", "Email patient summary to", "164.312(e)(1)"),
        "transfer": ("Hospital Transfer", "Transfer patient to", "164.310(a)(2)(iii)"),
        "courier": ("Courier Service", "Send records via courier to", "164.310(d)(1)"),
        "secure_msg": ("Secure Messaging", "Send secure message to", "164.312(e)(1)")
    }

    task_types = list(task_mapping.keys())
    assignments_created = 0

    for mrn in patient_mrns:
        task_type = random.choice(task_types)
        dir_type, action, hipaa = task_mapping[task_type]
        nurse = random.choice(nurses)

        # Find directory entries that match this task type
        matching_entries = [e for e in directory_entries if e[0] == dir_type]
        if matching_entries:
            target_entry = random.choice(matching_entries)
            target_value = target_entry[2]  # The specific contact (fax number, email, code, etc.)
            # Description only includes the name - user must look up details in Directory
            description = f"{action} '{target_entry[1]}' for patient {mrn}"
        else:
            target_value = "555-XXXX"
            description = f"{action} approved location for patient {mrn}"
        
        c.execute("""INSERT INTO assignments (task_type, patient_mrn, target_value, description, 
                     assigned_by, assigned_to, created_at, hipaa_section)
                     VALUES (?,?,?,?,?,?,?,?)""",
                 (task_type, mrn, target_value, description, session["user"], nurse,
                  datetime.now().strftime("%Y-%m-%d %H:%M"), hipaa))
        assignments_created += 1
    
    conn.commit()
    conn.close()
    return jsonify({"message": f"{assignments_created} assignments generated"})


@app.route("/api/assignments/<int:aid>/complete", methods=["POST"])
@nurse_only
def complete_assignment(aid):
    data = request.json
    user_value = data.get("user_value", "").strip()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT target_value, description, patient_mrn, task_type, hipaa_section FROM assignments WHERE id=?", (aid,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Assignment not found"}), 404
    
    target_value, description, patient_mrn, task_type, hipaa = row
    
    if user_value.lower() == target_value.lower():
        c.execute("UPDATE assignments SET status='Completed', completed_at=? WHERE id=?",
                 (datetime.now().strftime("%Y-%m-%d %H:%M"), aid))
        status = "Completed"
        # Log successful completion
        log_activity(session['user'], "ASSIGNMENT_COMPLETED", f"Completed assignment #{aid}: {description}", f"Patient: {patient_mrn}")
    else:
        c.execute("UPDATE assignments SET status='Failed', completed_at=? WHERE id=?",
                 (datetime.now().strftime("%Y-%m-%d %H:%M"), aid))

        violation_detail = f"Nurse {session['user']} submitted incorrect value '{user_value}' (expected '{target_value}') for task: {description}"
        enc_detail = cipher.encrypt(violation_detail.encode()).decode()

        c.execute("""INSERT INTO audit_results (type, severity, timestamp, details, recommendation,
                     hipaa_section, source, nurse_username)
                     VALUES (?,?,?,?,?,?,?,?)""",
                 (f"Incorrect {task_type.upper()}", "High", datetime.now().strftime("%Y-%m-%d %H:%M"),
                  enc_detail, "Review training and directory", hipaa, "nurse_violation", session["user"]))
        status = "Failed"
        # Log failed completion (violation created)
        log_activity(session['user'], "ASSIGNMENT_FAILED", f"Failed assignment #{aid}: Incorrect value submitted", f"Task: {description}, Expected: {target_value}, Got: {user_value}")

    conn.commit()
    conn.close()
    return jsonify({"message": f"Assignment {status.lower()}", "status": status})


# ---------------------------- Directory API ----------------------------
@app.route("/api/directory", methods=["GET"])
@login_required
def get_directory():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM directory ORDER BY type, name")
    rows = c.fetchall()
    conn.close()
    
    directory = []
    for row in rows:
        directory.append({
            "id": row[0], "type": row[1], "name": row[2],
            "value": row[3], "department": row[4], "notes": row[5]
        })
    return jsonify(directory)


# ---------------------------- Vulnerabilities API ----------------------------
@app.route("/api/vulnerabilities", methods=["GET"])
@login_required
def get_vulnerabilities():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, type, severity, timestamp, recommendation, hipaa_section FROM audit_results WHERE source='scanner'")
    rows = c.fetchall()
    conn.close()
    
    vulns = []
    for row in rows:
        vulns.append({
            "id": row[0], "type": row[1], "severity": row[2],
            "timestamp": row[3], "recommendation": row[4], "hipaa_section": row[5]
        })
    return jsonify(vulns)


@app.route("/api/seed_patients", methods=["POST"])
@admin_only
def seed_patients():
    """Generate 5 sample patients for demo"""
    sample_patients = [
        ("John", "Doe", "1965-03-15", "john.doe@email.com", "555-0101", "123-45-6789", "1428 Elm St, Springfield, IL 62701"),
        ("Jane", "Smith", "1978-07-22", "jane.smith@email.com", "555-0102", "234-56-7890", "892 Oak Ave, Springfield, IL 62702"),
        ("Robert", "Johnson", "1982-11-08", "robert.j@email.com", "555-0103", "345-67-8901", "3401 Maple Dr, Springfield, IL 62703"),
        ("Emily", "Davis", "1990-05-30", "emily.davis@email.com", "555-0104", "456-78-9012", "567 Pine Rd, Springfield, IL 62704"),
        ("Michael", "Wilson", "1975-09-14", "michael.w@email.com", "555-0105", "567-89-0123", "2100 Cedar Ln, Springfield, IL 62705")
    ]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    created = 0

    for first, last, dob, email, phone, ssn, address in sample_patients:
        mrn = generate_mrn()
        enc_ssn = cipher.encrypt(ssn.encode()).decode()
        try:
            c.execute("""INSERT INTO patients (mrn, first_name, last_name, date_of_birth, email, phone, address, ssn, created_at, created_by)
                         VALUES (?,?,?,?,?,?,?,?,?,?)""",
                     (mrn, first, last, dob, email, phone, address, enc_ssn, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session["user"]))
            created += 1
        except sqlite3.IntegrityError:
            continue  # Skip duplicates

    conn.commit()
    conn.close()

    log_activity(session["user"], "PATIENTS_SEEDED", f"{created} sample patients created", "Demo setup")

    return jsonify({"message": f"✅ {created} sample patients created!"})


@app.route("/api/seed_vulnerabilities", methods=["POST"])
@admin_only
def seed_vulnerabilities():
    vulns = [
        ("Weak Encryption","High","MD5 used for ePHI","Upgrade to AES-256-GCM","164.312(a)(2)(iv)"),
        ("No HTTPS","Critical","Data sent via HTTP","Enable TLS 1.3 + HSTS","164.312(e)(1)"),
        ("Unauthorized API Access","High","Open /patients endpoint","Add OAuth2 or API key","164.308(a)(3)(ii)(B)"),
        ("SQL Injection","Medium","Unvalidated input","Use parameterized queries","164.308(a)(1)(ii)(A)"),
        ("Insecure Dependencies","Low","Outdated Python modules","Run SBOM + patch/update","164.308(a)(1)(ii)(B)")
    ]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM audit_results WHERE source='scanner'")
    for t,s,d,r,h in vulns:
        enc = cipher.encrypt(d.encode()).decode()
        c.execute("INSERT INTO audit_results (type,severity,timestamp,details,recommendation,hipaa_section,source) VALUES (?,?,?,?,?,?,?)",
            (t,s,datetime.now().strftime("%Y-%m-%d %H:%M"),enc,r,h,"scanner"))
    conn.commit()
    conn.close()
    return jsonify({"message":"Technical vulnerabilities seeded"})


@app.route("/api/seed_nurse_violations", methods=["POST"])
@admin_only
def seed_nurse_violations():
    incidents = [
        ("Emailed PHI Externally","High","Nurse sent PHI to external email","Retrain + DLP filters","164.312(e)(1)"),
        ("Unauthorized Record Access","High","Nurse viewed patient record w/o authorization","Revoke access + monitor logs","164.308(a)(3)(ii)(B)"),
        ("Improper Device Usage","Medium","Copied PHI to personal USB","Block removable media","164.312(a)(2)(iv)"),
        ("Discussed Patient Info Publicly","Low","Spoke about PHI in hallway","Privacy training","164.308(a)(5)"),
        ("Faxed PHI to Wrong Office","Medium","Sent PHI to wrong fax #","Add verification step","164.312(b)")
    ]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for t,s,d,r,h in incidents:
        enc = cipher.encrypt(d.encode()).decode()
        c.execute("INSERT INTO audit_results (type,severity,timestamp,details,recommendation,hipaa_section,source) VALUES (?,?,?,?,?,?,?)",
            (t,s,datetime.now().strftime("%Y-%m-%d %H:%M"),enc,r,h,"nurse_violation"))
    conn.commit()
    conn.close()
    return jsonify({"message":"Nurse HIPAA violations seeded"})


@app.route("/api/seed_hipaa_compliance", methods=["POST"])
@admin_only
def seed_hipaa_compliance():
    """Seed comprehensive HIPAA compliance violations across all rule categories"""
    compliance_violations = [
        # Administrative Safeguards (164.308)
        ("Missing Risk Assessment", "Critical", "No HIPAA risk assessment conducted in past 12 months", "Conduct comprehensive risk assessment per 164.308(a)(1)(ii)(A)", "164.308(a)(1)(ii)(A)"),
        ("Inadequate Workforce Training", "High", "Only 40% of workforce completed HIPAA training", "Implement mandatory annual training program", "164.308(a)(5)(i)"),
        ("No Security Officer Designated", "Critical", "Organization lacks designated Security Officer", "Appoint qualified Security Officer immediately", "164.308(a)(2)"),
        ("Missing Sanction Policy", "High", "No documented sanction policy for HIPAA violations", "Create and implement sanction policy", "164.308(a)(1)(ii)(C)"),
        ("Incomplete BAA Contracts", "High", "3 vendors lack Business Associate Agreements", "Execute BAAs with all vendors handling ePHI", "164.308(b)(1)"),
        ("No Contingency Plan", "Critical", "Missing disaster recovery/contingency plan", "Develop and test contingency plan", "164.308(a)(7)(i)"),
        ("Inadequate Access Controls", "High", "No role-based access control implementation", "Implement least privilege access model", "164.308(a)(3)(i)"),
        ("Missing Incident Response", "Critical", "No breach notification procedures documented", "Create incident response plan per breach rules", "164.308(a)(6)(i)"),

        # Physical Safeguards (164.310)
        ("Unrestricted Facility Access", "High", "Server room lacks physical access controls", "Install badge reader and access logs", "164.310(a)(1)"),
        ("No Workstation Security", "Medium", "Unattended workstations not auto-locking", "Enable 5-minute screen lock policy", "164.310(b)"),
        ("Missing Device Inventory", "Medium", "No inventory of devices with ePHI access", "Create and maintain device inventory", "164.310(d)(1)"),
        ("Improper Media Disposal", "High", "Hard drives not sanitized before disposal", "Implement secure media disposal process", "164.310(d)(2)(i)"),
        ("Visitor Access Not Logged", "Low", "No visitor sign-in logs for secure areas", "Implement visitor management system", "164.310(a)(2)(iii)"),

        # Technical Safeguards (164.312)
        ("No Unique User IDs", "Critical", "Shared login credentials for staff", "Assign unique user IDs to each user", "164.312(a)(2)(i)"),
        ("Missing Audit Controls", "High", "System access not logged or monitored", "Enable comprehensive audit logging", "164.312(b)"),
        ("Weak Authentication", "Critical", "No multi-factor authentication for ePHI access", "Implement MFA for all ePHI systems", "164.312(d)"),
        ("Unencrypted Data at Rest", "Critical", "Patient database not encrypted", "Enable encryption for all ePHI at rest", "164.312(a)(2)(iv)"),
        ("Unencrypted Transmission", "Critical", "ePHI sent via unencrypted email", "Use encrypted channels (TLS 1.3+) for ePHI", "164.312(e)(1)"),
        ("No Automatic Logoff", "Medium", "Sessions don't timeout after inactivity", "Configure 15-minute session timeout", "164.312(a)(2)(iii)"),
        ("Missing Integrity Controls", "High", "No mechanism to detect data tampering", "Implement checksums/digital signatures", "164.312(c)(1)"),

        # Privacy Rule Violations (164.502-164.528)
        ("Missing Privacy Notice", "High", "Patients not provided Notice of Privacy Practices", "Provide NPP to all patients at first contact", "164.520(a)"),
        ("No Authorization Forms", "Medium", "Using outdated HIPAA authorization forms", "Update forms to meet all required elements", "164.508(c)"),
        ("Improper Minimum Necessary", "High", "Staff accessing full records when not needed", "Implement minimum necessary access controls", "164.502(b)"),
        ("Missing Patient Rights", "Medium", "No process for patients to request amendments", "Create patient rights request procedures", "164.526"),
        ("Accounting Failures", "Medium", "Cannot provide accounting of disclosures", "Implement disclosure tracking system", "164.528"),

        # Breach Notification Rule (164.400-164.414)
        ("Late Breach Notification", "Critical", "Breach discovered 45 days ago, not reported", "Notify HHS and affected individuals immediately", "164.408"),
        ("Incomplete Breach Assessment", "High", "No risk assessment for lost laptop", "Conduct 4-factor breach analysis", "164.402"),

        # Organizational Requirements
        ("Missing Policies & Procedures", "Critical", "HIPAA policies not documented", "Document all required P&Ps per spec", "164.316(a)"),
        ("No Policy Review Process", "Medium", "Policies not reviewed since 2019", "Implement annual policy review cycle", "164.316(b)(2)(iii)"),

        # Specific Use Cases
        ("Mobile Device Unencrypted", "High", "Staff phones with ePHI not encrypted", "Require device encryption or MDM solution", "164.312(a)(2)(iv)"),
        ("Cloud Storage Misconfiguration", "Critical", "Patient data in unsecured S3 bucket", "Review cloud security settings and enable encryption", "164.312(a)(1)"),
        ("Vendor Risk Not Assessed", "High", "Third-party EHR vendor not audited", "Conduct vendor security assessment", "164.308(b)(1)")
    ]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Clear existing compliance violations
    c.execute("DELETE FROM audit_results WHERE source='hipaa_compliance'")

    # Insert all compliance violations (organizational/system-wide - NOT assigned to individual nurses)
    # These should only appear in admin EDR panel, not in nurse "My Violations" page
    for violation_type, severity, details, recommendation, hipaa_section in compliance_violations:
        enc_details = cipher.encrypt(details.encode()).decode()

        # Calculate remediation deadline based on severity
        # Critical: 30 days, High: 60 days, Medium: 90 days, Low: 120 days
        days_to_remediate = {'Critical': 30, 'High': 60, 'Medium': 90, 'Low': 120}
        deadline_days = days_to_remediate.get(severity, 90)
        deadline_date = datetime.now() + timedelta(days=deadline_days)
        deadline = deadline_date.strftime("%Y-%m-%d")

        # nurse_username is NULL for organizational violations - only training/assignment violations get assigned to nurses
        c.execute(
            "INSERT INTO audit_results (type, severity, timestamp, details, recommendation, hipaa_section, source, status, nurse_username, remediation_deadline) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (violation_type, severity, datetime.now().strftime("%Y-%m-%d %H:%M"), enc_details, recommendation, hipaa_section, "hipaa_compliance", "Unresolved", None, deadline)
        )

    conn.commit()
    conn.close()

    return jsonify({
        "message": f"Successfully seeded {len(compliance_violations)} HIPAA compliance violations",
        "count": len(compliance_violations),
        "categories": {
            "Administrative": 8,
            "Physical": 5,
            "Technical": 7,
            "Privacy": 5,
            "Breach": 2,
            "Organizational": 2,
            "Specific": 3
        }
    })


# ---------------------------- EDR API ----------------------------
@app.route("/api/edr_data")
@login_required
def edr_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id,type,severity,timestamp,details,recommendation,hipaa_section,source,status,nurse_username FROM audit_results")
    rows = c.fetchall()
    conn.close()

    out = []
    for r in rows:
        try:
            detail = cipher.decrypt(r[4].encode()).decode()
        except:
            detail = "Decryption error"
        out.append({
            "id":r[0], "type":r[1], "severity":r[2], "timestamp":r[3],
            "details":detail, "recommendation":r[5], "hipaa_section":r[6],
            "source":r[7], "status":r[8], "nurse_username":r[9] or "N/A"
        })
    return jsonify(out)


@app.route("/api/audit/<int:aid>/resolve", methods=["POST"])
@login_required
def resolve_alert(aid):
    if session["role"] != "admin":
        return jsonify({"error":"read-only"}), 403
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE audit_results SET status='Resolved' WHERE id=?", (aid,))
    conn.commit()
    conn.close()
    return jsonify({"message":"Resolved"})


@app.route("/api/audit/reset_all", methods=["POST"])
@admin_only
def reset_all():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE audit_results SET status='Unresolved'")
    conn.commit()
    conn.close()
    return jsonify({"message":"All alerts reset"})


# ---------------------------- Nurse Violations API ----------------------------
@app.route("/api/my_violations")
@nurse_only
def my_violations():
    """Get violations assigned to the logged-in nurse"""
    username = session.get("user")  # Fixed: session key is "user", not "username"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, type, severity, timestamp, details, recommendation,
               hipaa_section, source, status, acknowledged_at, acknowledged_by, remediation_deadline
        FROM audit_results
        WHERE nurse_username=?
        ORDER BY timestamp DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()

    violations = []
    for r in rows:
        try:
            detail = cipher.decrypt(r[4].encode()).decode()
        except:
            detail = "Decryption error"

        # Check if overdue
        is_overdue = False
        days_until_deadline = None
        if r[11]:  # remediation_deadline
            try:
                deadline = datetime.strptime(r[11], "%Y-%m-%d")
                today = datetime.now()
                days_until_deadline = (deadline - today).days
                is_overdue = days_until_deadline < 0
            except:
                pass

        violations.append({
            "id": r[0],
            "type": r[1],
            "severity": r[2],
            "timestamp": r[3],
            "details": detail,
            "recommendation": r[5],
            "hipaa_section": r[6],
            "source": r[7],
            "status": r[8],
            "acknowledged_at": r[9],
            "acknowledged_by": r[10],
            "remediation_deadline": r[11],
            "is_acknowledged": r[9] is not None,
            "is_overdue": is_overdue,
            "days_until_deadline": days_until_deadline
        })
    return jsonify(violations)


@app.route("/api/violations/<int:vid>/acknowledge", methods=["POST"])
@nurse_only
def acknowledge_violation(vid):
    """Acknowledge a violation"""
    username = session.get("username")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if violation belongs to this nurse
    c.execute("SELECT nurse_username FROM audit_results WHERE id=?", (vid,))
    row = c.fetchone()
    if not row or row[0] != username:
        conn.close()
        return jsonify({"error": "Violation not found or not assigned to you"}), 403

    # Get violation details for logging
    c.execute("SELECT type, severity FROM audit_results WHERE id=?", (vid,))
    violation_info = c.fetchone()

    # Update acknowledgment
    c.execute("""
        UPDATE audit_results
        SET acknowledged_at=?, acknowledged_by=?, status='Acknowledged'
        WHERE id=?
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username, vid))
    conn.commit()
    conn.close()

    # Log activity
    if violation_info:
        v_type, v_severity = violation_info
        log_activity(username, "VIOLATION_ACKNOWLEDGED", f"Acknowledged {v_severity} violation: {v_type}", f"Violation ID: {vid}")

    return jsonify({"message": "Violation acknowledged successfully"})


@app.route("/api/violations/generate_signed_pdf", methods=["POST"])
@nurse_only
def generate_signed_pdf():
    """Generate a signed PDF of all nurse's violations"""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    import io

    username = session.get("username")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get all violations for this nurse
    c.execute("""
        SELECT id, type, severity, timestamp, details, recommendation,
               hipaa_section, status, acknowledged_at
        FROM audit_results
        WHERE nurse_username=?
        ORDER BY timestamp DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()

    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    story.append(Paragraph("HIPAA VIOLATIONS - PERSONAL ACKNOWLEDGMENT", title_style))
    story.append(Spacer(1, 0.3*inch))

    # Header info
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=12, spaceAfter=6)
    story.append(Paragraph(f"<b>Employee:</b> {username}", header_style))
    story.append(Paragraph(f"<b>Date Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", header_style))
    story.append(Paragraph(f"<b>Total Violations:</b> {len(rows)}", header_style))
    acknowledged_count = sum(1 for r in rows if r[8] is not None)
    story.append(Paragraph(f"<b>Acknowledged:</b> {acknowledged_count} / {len(rows)}", header_style))
    story.append(Spacer(1, 0.3*inch))

    # Add each violation
    for idx, r in enumerate(rows, 1):
        try:
            detail = cipher.decrypt(r[4].encode()).decode()
        except:
            detail = "Decryption error"

        severity_color = {
            'Critical': colors.red,
            'High': colors.orange,
            'Medium': colors.yellow,
            'Low': colors.green
        }.get(r[2], colors.grey)

        # Violation header
        violation_title = Paragraph(
            f"<b>Violation #{idx}: [{r[2]}] {r[1]}</b>",
            ParagraphStyle('ViolationTitle', parent=styles['Heading2'], fontSize=14, textColor=severity_color)
        )
        story.append(violation_title)

        # Violation details table
        data = [
            ["Timestamp:", r[3]],
            ["HIPAA Section:", r[6]],
            ["Status:", r[7]],
            ["What Happened:", detail],
            ["How to Remediate:", r[5]],
        ]

        if r[8]:  # acknowledged_at
            data.append(["Acknowledged:", r[8]])

        violation_table = Table(data, colWidths=[1.5*inch, 5*inch])
        violation_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONT', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(violation_table)
        story.append(Spacer(1, 0.2*inch))

        # Add page break every 2 violations
        if idx % 2 == 0 and idx < len(rows):
            story.append(PageBreak())

    # Signature section
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("<b>EMPLOYEE ACKNOWLEDGMENT</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        f"I, {username}, acknowledge that I have reviewed all {len(rows)} HIPAA violations listed in this document. "
        f"I understand the severity of these violations and commit to following proper HIPAA procedures moving forward.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))

    sig_data = [
        ["Employee Signature:", "_" * 40, "Date:", "_" * 20],
        ["", f"{username} (Electronic Signature)", "", datetime.now().strftime('%Y-%m-%d')],
    ]
    sig_table = Table(sig_data, colWidths=[1.5*inch, 2.5*inch, 0.7*inch, 1.8*inch])
    sig_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONT', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (1, 1), 'CENTER'),
        ('ALIGN', (3, 1), (3, 1), 'CENTER'),
    ]))
    story.append(sig_table)

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    # Return PDF
    from flask import send_file as flask_send_file
    return flask_send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'HIPAA_Violations_{username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )


# ---------------------------- Reports API ----------------------------
@app.route("/api/generate_report", methods=["POST"])
@admin_only
def generate_report_api():
    try:
        from generate_report import generate_pdf_report, fetch_hipaa_violations
        violations = fetch_hipaa_violations()
        generate_pdf_report(violations=violations)
        return jsonify({"message": "HIPAA Violations Report generated successfully", "count": len(violations)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reports/download", methods=["GET"])
@admin_only
def download_report():
    try:
        return send_file("HIPAA_Violations_Report.pdf", as_attachment=True)
    except:
        return jsonify({"error": "Report not found. Please generate the report first."}), 404


# ---------------------------- Scanner API ----------------------------
@app.route("/api/scanner/run", methods=["POST"])
@login_required
def run_scanner():
    results = {
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "vulnerabilities_found": 4,
        "findings": [
            {"type": "SQL Injection", "severity": "High", "location": "login endpoint"},
            {"type": "Weak Password Policy", "severity": "Medium", "location": "user registration"},
            {"type": "Missing HTTPS", "severity": "Critical", "location": "all endpoints"},
            {"type": "Unencrypted PHI", "severity": "Critical", "location": "patient records"}
        ]
    }
    return jsonify(results)


# ---------------------------- Audit Trail ----------------------------
@app.route("/audit_trail")
@admin_only
def audit_trail_page():
    """Display audit trail page"""
    return render_template("audit_trail.html")


@app.route("/api/audit_trail", methods=["GET"])
@admin_only
def get_audit_trail():
    """Get all activity logs with optional filtering"""
    action_type = request.args.get("action_type", "")
    username = request.args.get("username", "")
    limit = request.args.get("limit", "100")

    try:
        limit = int(limit)
    except:
        limit = 100

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    query = "SELECT id, timestamp, username, action_type, description, details, ip_address FROM activity_log"
    params = []
    filters = []

    if action_type:
        filters.append("action_type = ?")
        params.append(action_type)

    if username:
        filters.append("username = ?")
        params.append(username)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "id": r[0],
            "timestamp": r[1],
            "username": r[2],
            "action_type": r[3],
            "description": r[4],
            "details": r[5],
            "ip_address": r[6]
        })

    return jsonify(logs)


# ---------------------------- Training Simulator ----------------------------
@app.route("/training_simulator")
@login_required
def training_simulator_page():
    return render_template("training_simulator.html")


@app.route("/api/training/score", methods=["GET"])
@login_required
def get_training_score():
    """Get current user's compliance score and completed modules"""
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT compliance_score, training_completed, last_training_date, completed_modules FROM users WHERE username=?",
              (session["user"],))
    result = c.fetchone()
    conn.close()

    if result:
        completed_modules = json.loads(result[3] or '[]')
        return jsonify({
            "compliance_score": result[0] or 0,
            "training_completed": result[1] or 0,
            "last_training_date": result[2],
            "completed_modules": completed_modules
        })
    return jsonify({"compliance_score": 0, "training_completed": 0, "last_training_date": None, "completed_modules": []})


@app.route("/api/training/submit_quiz", methods=["POST"])
@login_required
def submit_quiz():
    """Submit entire quiz at once - all questions together"""
    import json
    data = request.json
    module_name = data.get("module_name")  # e.g., "phi_protection", "secure_communication", "breach_prevention"
    answers = data.get("answers", [])  # List of {scenario_type, is_correct}

    conn = sqlite3.connect(DB_PATH, timeout=10)
    c = conn.cursor()

    # Count correct answers in this submission
    quiz_correct = sum(1 for ans in answers if ans.get("is_correct"))
    quiz_total = len(answers)

    # Count total correct and total questions answered from activity log
    c.execute("""SELECT COUNT(*) FROM activity_log
                 WHERE username=? AND action_type='TRAINING_COMPLETED' AND details LIKE '%Correct%'""",
              (session["user"],))
    prev_correct = c.fetchone()[0] or 0

    c.execute("""SELECT COUNT(*) FROM activity_log
                 WHERE username=? AND action_type='TRAINING_COMPLETED'""",
              (session["user"],))
    prev_total = c.fetchone()[0] or 0

    # Calculate new totals
    total_correct = prev_correct + quiz_correct
    total_answered = prev_total + quiz_total

    # Get current completed_modules from database
    c.execute("SELECT completed_modules FROM users WHERE username=?", (session["user"],))
    result = c.fetchone()
    completed_modules = json.loads(result[0] or '[]') if result else []

    # Mark module as completed if passing score (at least 2 out of 3 correct)
    passing_score = 2 if quiz_total >= 3 else 1
    if quiz_correct >= passing_score and module_name and module_name not in completed_modules:
        completed_modules.append(module_name)

    # Calculate percentage based on completed modules (each module = 33.33%)
    # This rewards module completion rather than just individual question accuracy
    TOTAL_MODULES = 3
    new_score = round((len(completed_modules) / TOTAL_MODULES) * 100)

    # Update user record
    c.execute("""UPDATE users
                 SET compliance_score=?, training_completed=?, last_training_date=?, completed_modules=?
                 WHERE username=?""",
              (new_score, total_answered, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               json.dumps(completed_modules), session["user"]))

    # Log each answer to activity log
    for ans in answers:
        is_correct = ans.get("is_correct", False)
        scenario_type = ans.get("scenario_type", "unknown")

        log_activity(session["user"], "TRAINING_COMPLETED",
                    f"Training module '{scenario_type}' completed",
                    f"Result: {'Correct' if is_correct else 'Incorrect'}, Module: {module_name}")

        # If incorrect, create a violation
        if not is_correct:
            enc_detail = cipher.encrypt(f"Failed training scenario: {scenario_type}".encode()).decode()
            c.execute("""INSERT INTO audit_results (type, severity, timestamp, details, recommendation,
                         hipaa_section, source, nurse_username)
                         VALUES (?,?,?,?,?,?,?,?)""",
                     (f"Training Violation: {scenario_type}", "Medium",
                      datetime.now().strftime("%Y-%m-%d %H:%M"),
                      enc_detail, "Complete additional training", "164.308(a)(5)",
                      "training_simulator", session["user"]))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "new_score": new_score,
        "quiz_correct": quiz_correct,
        "quiz_total": quiz_total,
        "total_correct": total_correct,
        "total_answered": total_answered,
        "completed_modules": completed_modules
    })


@app.route("/api/training/submit", methods=["POST"])
@login_required
def submit_training():
    """Legacy endpoint - redirects to submit_quiz for backwards compatibility"""
    return jsonify({"error": "Please use /api/training/submit_quiz endpoint"}), 400


@app.route("/api/training/reset/<username>", methods=["POST"])
@login_required
def reset_user_training(username):
    """Reset training progress for a specific user (not admin)"""
    # Prevent resetting admin
    if username == "admin":
        return jsonify({"error": "Cannot reset admin training"}), 403

    # Users can only reset their own training, or admins can reset any nurse
    if session["user"] != username and session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""UPDATE users
                 SET compliance_score=0, training_completed=0, last_training_date=NULL
                 WHERE username=? AND role='user'""",
              (username,))
    conn.commit()
    conn.close()

    log_activity(session["user"], "TRAINING_RESET", f"Training progress reset for user: {username}", "")

    return jsonify({"message": f"Training progress reset for {username}"})


# ---------------------------- Data Breach Simulation ----------------------------
@app.route("/api/breach/simulate", methods=["POST"])
@admin_only
def simulate_breach():
    """Simulate a data breach incident for training/demo purposes"""
    try:
        data = request.get_json()
        if not data:
            data = {}
        breach_type = data.get("breach_type", "ransomware")
        affected_records = data.get("affected_records", 100)
    except Exception as e:
        return jsonify({"error": f"Invalid request: {str(e)}"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    breach_scenarios = {
        "ransomware": {
            "type": "RANSOMWARE ATTACK",
            "severity": "Critical",
            "details": f"Ransomware encrypted {affected_records} patient records. Attackers demand $50,000 Bitcoin payment. Systems locked.",
            "recommendation": "DO NOT PAY. Activate incident response team, isolate infected systems, restore from backups, notify HHS within 60 days",
            "hipaa": "164.308(a)(6)(ii)"
        },
        "insider_threat": {
            "type": "INSIDER DATA THEFT",
            "severity": "Critical",
            "details": f"Employee downloaded {affected_records} patient records to personal device before resignation. PHI compromised.",
            "recommendation": "Terminate access immediately, conduct forensic investigation, notify affected patients, file police report",
            "hipaa": "164.308(a)(3)(ii)(A)"
        },
        "phishing": {
            "type": "PHISHING ATTACK - CREDENTIALS COMPROMISED",
            "severity": "High",
            "details": f"5 employees fell for phishing email. Attacker accessed {affected_records} patient records via stolen credentials.",
            "recommendation": "Reset all passwords, enable MFA, conduct phishing awareness training, monitor for unauthorized access",
            "hipaa": "164.308(a)(5)(ii)(B)"
        },
        "database_exposure": {
            "type": "DATABASE EXPOSED TO INTERNET",
            "severity": "Critical",
            "details": f"Misconfigured database exposed {affected_records} patient records publicly for 30 days. Search engines indexed data.",
            "recommendation": "Secure database immediately, request search engine delisting, notify HHS and affected individuals within 60 days",
            "hipaa": "164.312(a)(1)"
        },
        "physical_theft": {
            "type": "LAPTOP THEFT WITH UNENCRYPTED PHI",
            "severity": "High",
            "details": f"Unencrypted laptop stolen from employee vehicle containing {affected_records} patient records.",
            "recommendation": "File police report, notify affected patients, implement mandatory encryption policy, remote wipe if possible",
            "hipaa": "164.312(a)(2)(iv)"
        }
    }

    scenario = breach_scenarios.get(breach_type, breach_scenarios["ransomware"])
    enc_detail = cipher.encrypt(scenario["details"].encode()).decode()

    # Create the breach incident
    c.execute("""INSERT INTO audit_results (type, severity, timestamp, details, recommendation,
                 hipaa_section, source, status)
                 VALUES (?,?,?,?,?,?,?,?)""",
             (scenario["type"], scenario["severity"],
              datetime.now().strftime("%Y-%m-%d %H:%M"),
              enc_detail, scenario["recommendation"],
              scenario["hipaa"], "breach_simulation", "Unresolved"))

    breach_id = c.lastrowid

    # Log the breach simulation
    log_activity(session["user"], "BREACH_SIMULATED",
                f"Data breach simulation initiated: {scenario['type']}",
                f"Affected records: {affected_records}")

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "breach_id": breach_id,
        "message": f"Breach simulation created: {scenario['type']}",
        "breach_details": scenario
    })


# ---------------------------- Demo/Presentation Tools ----------------------------
@app.route("/api/reset_demo", methods=["POST"])
@admin_only
def reset_demo():
    """Reset database to demo state - deletes all data and re-initializes"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Clear all tables except users
        c.execute("DELETE FROM patients")
        c.execute("DELETE FROM assignments")
        c.execute("DELETE FROM audit_results")
        c.execute("DELETE FROM directory")
        c.execute("DELETE FROM activity_log")

        # Reset user training scores and completed modules
        c.execute("UPDATE users SET compliance_score=0, training_completed=0, last_training_date=NULL, completed_modules='[]' WHERE role='user'")

        # reset all passwords back to default lol
        c.execute("UPDATE users SET password=? WHERE username='admin'", (hash_pw("Admin123!"),))
        c.execute("UPDATE users SET password=? WHERE username='stefan'", (hash_pw("Stefan123!"),))
        c.execute("UPDATE users SET password=? WHERE username='ana'", (hash_pw("Ana123!"),))
        c.execute("UPDATE users SET password=? WHERE username='jordan'", (hash_pw("Jordan123!"),))
        c.execute("UPDATE users SET password=? WHERE username='jeremiah'", (hash_pw("Jeremiah123!"),))
        c.execute("UPDATE users SET password=? WHERE username='mumin'", (hash_pw("Mumin123!"),))

        # Re-add directory entries (25 entries - 5 per category)
        directory_entries = [
            # Fax Approved (5 entries)
            ('Fax Approved', 'St. Mary\'s Hospital - Radiology', '(555) 723-4400', 'Radiology', '1200 Medical Center Dr, Building A, Floor 2'),
            ('Fax Approved', 'City General - Cardiology Dept', '(555) 892-1155', 'Cardiology', '450 Healthcare Plaza, Suite 300, Springfield, IL 62701'),
            ('Fax Approved', 'SecureMed Billing Department', '(555) 234-2000', 'Billing', 'Internal - 789 Admin Blvd, Room 105'),
            ('Fax Approved', 'Valley Orthopedics Center', '(555) 456-7890', 'Orthopedics', '890 Medical Park Way, Building 3, Springfield, IL 62703'),
            ('Fax Approved', 'Regional Laboratory Services', '(555) 334-8899', 'Laboratory', '220 Science Blvd, Floor 1, Springfield, IL 62705'),
            # Email Secure (5 entries)
            ('Email Secure', 'Medical Records Department', 'records@securemed.internal', 'Records', 'Use encrypted email only - Internal system'),
            ('Email Secure', 'Insurance Pre-Authorization', 'preauth@securemed.internal', 'Insurance', 'For insurance claims and pre-auth requests'),
            ('Email Secure', 'Lab Results Coordination', 'labresults@securemed.internal', 'Laboratory', 'Secure portal for lab result transmission'),
            ('Email Secure', 'Specialist Referrals', 'referrals@securemed.internal', 'Care Coordination', 'For specialist consultation requests'),
            ('Email Secure', 'Imaging Department', 'imaging@securemed.internal', 'Radiology', 'CT, MRI, and X-ray report distribution'),
            # Hospital Transfer (5 entries)
            ('Hospital Transfer', 'St. Mary\'s Hospital - Emergency', '2500 Medical Center Dr, Springfield, IL 62702', 'Emergency', 'ER Receiving - Use secure transfer line (555) 723-4911'),
            ('Hospital Transfer', 'Regional Medical Center - ICU', '3400 Healthcare Pkwy, Building C, Floor 4, Springfield, IL 62704', 'Critical Care', 'Contact Charge Nurse at (555) 445-7800 before transfer'),
            ('Hospital Transfer', 'Downtown Specialty Clinic', '125 Main Street, Suite 200, Springfield, IL 62701', 'Specialists', 'Referrals for Cardiology, Neurology, Oncology'),
            ('Hospital Transfer', 'Memorial Hospital - Surgical Unit', '5600 University Ave, Springfield, IL 62706', 'Surgery', 'Pre-surgical admissions - Call (555) 667-3200 ext. 401'),
            ('Hospital Transfer', 'Springfield Rehabilitation Center', '1880 Wellness Drive, Springfield, IL 62708', 'Rehabilitation', 'Physical therapy and post-acute care'),
            # Courier Service (5 entries)
            ('Courier Service', 'MedCourier Express', 'Pickup: Building C Main Entrance, 789 Admin Blvd', 'Logistics', 'Scheduled pickups M-F 10am, 2pm, 5pm - Call (555) 768-2100'),
            ('Courier Service', 'SecureTransport Medical', 'Drop-off: Loading Dock B, Rear of Building A', 'Logistics', 'HIPAA-compliant transport - Tracking # required'),
            ('Courier Service', 'QuickMed Delivery Service', '450 Healthcare Plaza, Central Receiving', 'Logistics', 'Same-day delivery within 5 miles - (555) 892-3344'),
            ('Courier Service', 'Priority Health Logistics', '789 Admin Blvd, Suite 100', 'Logistics', 'Overnight delivery available - Temperature controlled'),
            ('Courier Service', 'CareLink Transport Services', 'Central Hub: 3200 Distribution Pkwy', 'Logistics', 'Multi-facility routing - Call (555) 445-9900 for scheduling'),
            # Secure Messaging (5 entries)
            ('Secure Messaging', 'Dr. Sarah Chen - Internal Medicine', 'SM-1847', 'Internal Medicine', 'Secure message via internal system - Patient consults'),
            ('Secure Messaging', 'Pharmacy - Prescription Refills', 'RX-4402', 'Pharmacy', 'Use for prescription renewals and clarifications'),
            ('Secure Messaging', 'Care Coordination Team', 'MSG-7733', 'Care Management', 'Discharge planning and follow-up coordination'),
            ('Secure Messaging', 'Dr. Michael Roberts - Cardiology', 'CARD-8821', 'Cardiology', 'Cardiac consultation and follow-up'),
            ('Secure Messaging', 'Nurse Practitioner - Primary Care', 'NP-5544', 'Primary Care', 'Routine follow-ups and medication management')
        ]
        c.executemany("INSERT INTO directory (type,name,value,department,notes) VALUES (?,?,?,?,?)", directory_entries)

        conn.commit()
        conn.close()

        # Log the reset
        log_activity(session["user"], "DEMO_RESET", "Database reset to demo state", "All data cleared, directory re-initialized, no patients created")

        return jsonify({"message": "Database reset successfully! Use Quick Setup to generate demo data."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------- Main ----------------------------
if __name__ == "__main__":
    print("ðŸš€ SecureMed running on http://127.0.0.1:5000/login")
    print("   [Credentials hidden for security]")
    print("   Check CREDENTIALS.txt for login info")
    app.run(debug=True, port=5000)