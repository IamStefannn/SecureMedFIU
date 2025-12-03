import sqlite3
import random
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import os

DB_PATH = 'securemed.db'
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "qIkBRr-hIef_oyohOmekF3N_lvAmNmo0xceLQqDO-AQ=")
cipher = Fernet(ENCRYPTION_KEY.encode())

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# make random date from last 30 days
def random_date_last_30_days():
    days_ago = random.randint(0, 30)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d %H:%M")

# generate unique mrn
def generate_unique_mrn():
    while True:
        mrn = f"MRN{random.randint(1000, 9999)}"
        c.execute("SELECT id FROM patients WHERE mrn=?", (mrn,))
        if not c.fetchone():
            return mrn

print("Starting realistic data seeding...")
print("=" * 60)

# add 15 patients
print("\n1. Adding 15 realistic patients...")

# delete old sample patients
c.execute("DELETE FROM patients WHERE created_by='admin'")

realistic_patients = [
    ("Emily", "Rodriguez", "1985-03-15", "emily.rodriguez@email.com", "555-0123", "234-56-7890", "142 Maple Ave, Springfield, IL 62701"),
    ("Michael", "Thompson", "1978-11-22", "m.thompson@email.com", "555-0124", "345-67-8901", "789 Oak Street, Springfield, IL 62702"),
    ("Sarah", "Williams", "1992-07-08", "sarah.w@email.com", "555-0125", "456-78-9012", "1523 Pine Rd, Springfield, IL 62703"),
    ("David", "Chen", "1965-09-30", "david.chen@email.com", "555-0126", "567-89-0123", "456 Cedar Ln, Springfield, IL 62704"),
    ("Jennifer", "Martinez", "1988-02-14", "jen.martinez@email.com", "555-0127", "678-90-1234", "2890 Birch Dr, Springfield, IL 62705"),
    ("Robert", "Anderson", "1955-12-05", "r.anderson@email.com", "555-0128", "789-01-2345", "567 Elm St, Springfield, IL 62706"),
    ("Lisa", "Taylor", "1990-06-18", "lisa.taylor@email.com", "555-0129", "890-12-3456", "3401 Walnut Ave, Springfield, IL 62707"),
    ("James", "White", "1972-04-25", "james.white@email.com", "555-0130", "901-23-4567", "198 Cherry Ln, Springfield, IL 62708"),
    ("Patricia", "Harris", "1983-10-12", "pat.harris@email.com", "555-0131", "012-34-5678", "2345 Ash Street, Springfield, IL 62709"),
    ("Christopher", "Lee", "1995-01-07", "chris.lee@email.com", "555-0132", "123-45-6789", "678 Hickory Dr, Springfield, IL 62710"),
    ("Nancy", "Walker", "1960-08-20", "nancy.walker@email.com", "555-0133", "234-56-7801", "4501 Willow Rd, Springfield, IL 62711"),
    ("Daniel", "Hall", "1987-05-03", "dan.hall@email.com", "555-0134", "345-67-8912", "890 Spruce Ave, Springfield, IL 62712"),
    ("Karen", "Young", "1975-11-28", "karen.young@email.com", "555-0135", "456-78-9023", "1234 Poplar Ln, Springfield, IL 62713"),
    ("Matthew", "King", "1993-09-16", "matt.king@email.com", "555-0136", "567-89-0134", "5678 Beech St, Springfield, IL 62714"),
    ("Betty", "Wright", "1958-03-09", "betty.wright@email.com", "555-0137", "678-90-1245", "901 Sycamore Dr, Springfield, IL 62715")
]

for first, last, dob, email, phone, ssn, address in realistic_patients:
    mrn = generate_unique_mrn()
    enc_ssn = cipher.encrypt(ssn.encode()).decode()
    created_at = random_date_last_30_days()
    c.execute("""INSERT INTO patients (mrn, first_name, last_name, date_of_birth, email, phone, address, ssn, created_by, created_at)
                 VALUES (?,?,?,?,?,?,?,?,?,?)""",
             (mrn, first, last, dob, email, phone, address, enc_ssn, 'admin', created_at))

print(f"   Added {len(realistic_patients)} patients with realistic data")

# add 30 assignments
print("\n2. Adding 30 realistic assignments...")

# get patient mrns
c.execute("SELECT mrn FROM patients")
patient_mrns = [row[0] for row in c.fetchall()]

# get nurses
c.execute("SELECT username FROM users WHERE role='user'")
nurses = [row[0] for row in c.fetchall()]
if not nurses:
    nurses = ['nurse', 'nurse2']

# get directory values so assignments match
c.execute("SELECT value FROM directory WHERE type='Fax Approved'")
fax_numbers = [row[0] for row in c.fetchall()]

c.execute("SELECT value FROM directory WHERE type='Email Secure'")
email_addresses = [row[0] for row in c.fetchall()]

c.execute("SELECT value FROM directory WHERE type='Hospital Transfer'")
transfer_locations = [row[0] for row in c.fetchall()]

c.execute("SELECT value FROM directory WHERE type='Courier Service'")
courier_addresses = [row[0] for row in c.fetchall()]

c.execute("SELECT value FROM directory WHERE type='Secure Messaging'")
secure_msg_codes = [row[0] for row in c.fetchall()]

# assignment templates using actual directory values
assignment_templates = [
    ("fax", "Fax patient records to {} for patient {}", "164.312(e)(1)", fax_numbers),
    ("email", "Send secure email to {} for patient {}", "164.312(e)(1)", email_addresses),
    ("transfer", "Transfer patient {} to {}", "164.502(a)(1)", transfer_locations),
    ("courier", "Send physical records to {} for patient {}", "164.310(d)(1)", courier_addresses),
    ("secure_msg", "Send secure message using code {} for patient {}", "164.312(e)(2)", secure_msg_codes)
]

# clear old assignments
c.execute("DELETE FROM assignments")

for i in range(30):
    task_type, desc_template, hipaa, targets = random.choice(assignment_templates)
    mrn = random.choice(patient_mrns)
    target = random.choice(targets)
    assigned_to = random.choice(nurses)
    created_at = random_date_last_30_days()

    description = desc_template.format(target, mrn)

    # 70% pending 30% completed
    if random.random() < 0.7:
        status = "Pending"
        completed_at = None
    else:
        status = "Completed"
        completed_days_ago = random.randint(0, 15)
        completed_date = datetime.now() - timedelta(days=completed_days_ago)
        completed_at = completed_date.strftime("%Y-%m-%d %H:%M")

    c.execute("""INSERT INTO assignments (task_type, patient_mrn, target_value, description,
                 assigned_by, assigned_to, status, created_at, completed_at, hipaa_section)
                 VALUES (?,?,?,?,?,?,?,?,?,?)""",
             (task_type, mrn, target, description, 'admin', assigned_to, status, created_at, completed_at, hipaa))

print(f"   Added 30 assignments (mix of pending and completed)")

# spread timestamps over 30 days
print("\n3. Spreading data timestamps over last 30 days...")
print("   Patients: Created dates vary")
print("   Assignments: Created dates vary")
print("   Some assignments already completed")

conn.commit()
conn.close()

print("\n" + "=" * 60)
print("REALISTIC DATA SEEDING COMPLETE!")
print("=" * 60)
print("\nSummary:")
print(f"  - 15 patients with realistic names, emails, phones, SSNs")
print(f"  - 30 assignments spread over last 30 days")
print(f"  - Mix of pending ({30*0.7:.0f}) and completed ({30*0.3:.0f}) assignments")
print(f"  - Assigned to: {', '.join(nurses)}")
print(f"  - All timestamps distributed across last 30 days")
