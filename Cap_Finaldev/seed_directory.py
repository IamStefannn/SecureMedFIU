import sqlite3

DB_PATH = 'securemed.db'
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# delete old directory stuff
c.execute('DELETE FROM directory')

# realistic directory entries - 5 per type
directory_entries = [
    # fax approved locations
    ('Fax Approved', 'St. Mary\'s Hospital - Radiology', '(555) 723-4400', 'Radiology', '1200 Medical Center Dr, Building A, Floor 2'),
    ('Fax Approved', 'City General - Cardiology Dept', '(555) 892-1155', 'Cardiology', '450 Healthcare Plaza, Suite 300, Springfield, IL 62701'),
    ('Fax Approved', 'SecureMed Billing Department', '(555) 234-2000', 'Billing', 'Internal - 789 Admin Blvd, Room 105'),
    ('Fax Approved', 'Valley Orthopedics Center', '(555) 456-7890', 'Orthopedics', '890 Medical Park Way, Building 3, Springfield, IL 62703'),
    ('Fax Approved', 'Regional Laboratory Services', '(555) 334-8899', 'Laboratory', '220 Science Blvd, Floor 1, Springfield, IL 62705'),

    # secure emails
    ('Email Secure', 'Medical Records Department', 'records@securemed.internal', 'Records', 'Use encrypted email only - Internal system'),
    ('Email Secure', 'Insurance Pre-Authorization', 'preauth@securemed.internal', 'Insurance', 'For insurance claims and pre-auth requests'),
    ('Email Secure', 'Lab Results Coordination', 'labresults@securemed.internal', 'Laboratory', 'Secure portal for lab result transmission'),
    ('Email Secure', 'Specialist Referrals', 'referrals@securemed.internal', 'Care Coordination', 'For specialist consultation requests'),
    ('Email Secure', 'Imaging Department', 'imaging@securemed.internal', 'Radiology', 'CT, MRI, and X-ray report distribution'),

    # hospital transfer places
    ('Hospital Transfer', 'St. Mary\'s Hospital - Emergency', '2500 Medical Center Dr, Springfield, IL 62702', 'Emergency', 'ER Receiving - Use secure transfer line (555) 723-4911'),
    ('Hospital Transfer', 'Regional Medical Center - ICU', '3400 Healthcare Pkwy, Building C, Floor 4, Springfield, IL 62704', 'Critical Care', 'Contact Charge Nurse at (555) 445-7800 before transfer'),
    ('Hospital Transfer', 'Downtown Specialty Clinic', '125 Main Street, Suite 200, Springfield, IL 62701', 'Specialists', 'Referrals for Cardiology, Neurology, Oncology'),
    ('Hospital Transfer', 'Memorial Hospital - Surgical Unit', '5600 University Ave, Springfield, IL 62706', 'Surgery', 'Pre-surgical admissions - Call (555) 667-3200 ext. 401'),
    ('Hospital Transfer', 'Springfield Rehabilitation Center', '1880 Wellness Drive, Springfield, IL 62708', 'Rehabilitation', 'Physical therapy and post-acute care'),

    # courier services
    ('Courier Service', 'MedCourier Express', 'Pickup: Building C Main Entrance, 789 Admin Blvd', 'Logistics', 'Scheduled pickups M-F 10am, 2pm, 5pm - Call (555) 768-2100'),
    ('Courier Service', 'SecureTransport Medical', 'Drop-off: Loading Dock B, Rear of Building A', 'Logistics', 'HIPAA-compliant transport - Tracking # required'),
    ('Courier Service', 'QuickMed Delivery Service', '450 Healthcare Plaza, Central Receiving', 'Logistics', 'Same-day delivery within 5 miles - (555) 892-3344'),
    ('Courier Service', 'Priority Health Logistics', '789 Admin Blvd, Suite 100', 'Logistics', 'Overnight delivery available - Temperature controlled'),
    ('Courier Service', 'CareLink Transport Services', 'Central Hub: 3200 Distribution Pkwy', 'Logistics', 'Multi-facility routing - Call (555) 445-9900 for scheduling'),

    # secure messaging codes
    ('Secure Messaging', 'Dr. Sarah Chen - Internal Medicine', 'SM-1847', 'Internal Medicine', 'Secure message via internal system - Patient consults'),
    ('Secure Messaging', 'Pharmacy - Prescription Refills', 'RX-4402', 'Pharmacy', 'Use for prescription renewals and clarifications'),
    ('Secure Messaging', 'Care Coordination Team', 'MSG-7733', 'Care Management', 'Discharge planning and follow-up coordination'),
    ('Secure Messaging', 'Dr. Michael Roberts - Cardiology', 'CARD-8821', 'Cardiology', 'Cardiac consultation and follow-up'),
    ('Secure Messaging', 'Nurse Practitioner - Primary Care', 'NP-5544', 'Primary Care', 'Routine follow-ups and medication management')
]

# put them all in db
for entry in directory_entries:
    c.execute('''INSERT INTO directory (type, name, value, department, notes)
                 VALUES (?, ?, ?, ?, ?)''', entry)

conn.commit()
conn.close()

print(f'Successfully added {len(directory_entries)} directory entries!')
print('   - 5 Fax numbers')
print('   - 5 Email addresses')
print('   - 5 Hospital transfers')
print('   - 5 Courier services')
print('   - 5 Secure messaging contacts')
