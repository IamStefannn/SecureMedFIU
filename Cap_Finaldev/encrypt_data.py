import sqlite3
from cryptography.fernet import Fernet
import os

# get encryption key from env or just use default
encryption_key = os.environ.get('ENCRYPTION_KEY', 'qIkBRr-hIef_oyohOmekF3N_lvAmNmo0xceLQqDO-AQ=')
key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
cipher = Fernet(key)

# connect to db
conn = sqlite3.connect('securemed.db')
cursor = conn.cursor()

# check if recommendation column there, add it if not
try:
    cursor.execute('SELECT recommendation FROM audit_results LIMIT 1')
except sqlite3.OperationalError:
    print("Adding 'recommendation' column to audit_results table...")
    cursor.execute('ALTER TABLE audit_results ADD COLUMN recommendation TEXT')
    conn.commit()

# delete old stuff so we dont get duplicates
cursor.execute('DELETE FROM audit_results')

# mock data with recommendations
data = [
    ("Weak Encryption", "High", "2025-06-08",
     "Found in patient records endpoint",
     "Upgrade to AES-256-GCM encryption and implement proper key management system"),
    ("SQL Injection Risk", "Medium", "2025-06-08",
     "Detected in login form",
     "Use parameterized queries and implement input validation"),
    ("Missing Input Validation", "Medium", "2025-06-08",
     "User input not sanitized in search functionality",
     "Implement comprehensive input validation and sanitization"),
    ("Insufficient Access Controls", "Critical", "2025-06-08",
     "No authentication required for API endpoints",
     "Implement OAuth 2.0 or API key authentication"),
    ("No HTTPS Enforcement", "High", "2025-06-08",
     "Data transmitted over unencrypted HTTP",
     "Enable HTTPS with TLS 1.3 and implement HSTS headers")
]

for type_val, severity, timestamp, details, recommendation in data:
    encrypted = cipher.encrypt(details.encode()).decode()
    cursor.execute('''
        INSERT INTO audit_results (type, severity, timestamp, details, recommendation)
        VALUES (?, ?, ?, ?, ?)
    ''', (type_val, severity, timestamp, encrypted, recommendation))

print(f"✅ Inserted {len(data)} vulnerability records with recommendations")

# test decrypt to make sure it works
cursor.execute('SELECT details, recommendation FROM audit_results ORDER BY id LIMIT 1')
row = cursor.fetchone()

if row:
    decrypted = cipher.decrypt(row[0].encode()).decode()
    print(f"✅ Decrypted details for first record: {decrypted}")
    print(f"✅ Recommendation: {row[1]}")
else:
    print("❌ No records found to decrypt.")

conn.commit()
conn.close()

print(f"\n✅ Database updated successfully!")
print(f"   Using encryption key from: {'environment variable' if os.environ.get('ENCRYPTION_KEY') else 'default (development only)'}")
