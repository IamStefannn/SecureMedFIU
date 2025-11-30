# Project Documentation
## SecureMed Healthcare Cybersecurity Platform

**Team:** Stefan Dumitrasku, Ana Salazar, Jordan Burgos, Jeremiah Luzincourt, Mumin Tahir
**Version:** 1.0.0
**Project Duration:** 8 weeks (4 sprints × 2 weeks)
**Last Updated:** November 25, 2024

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [API Reference](#api-reference)
3. [Deployment Guide](#deployment-guide)
4. [Product Backlog](#product-backlog)
5. [Scrum Evidence](#scrum-evidence)
6. [Team Contributions](#team-contributions)

---

## Architecture Overview

### System Architecture (C4 Container Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                         SecureMed Platform                       │
│                   (Healthcare HIPAA Compliance System)           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  LEVEL 1: SYSTEM CONTEXT                                        │
│                                                                  │
│  ┌──────────┐         ┌─────────────────┐       ┌──────────┐  │
│  │   Admin  │◄───────►│   SecureMed     │◄─────►│  Auditor │  │
│  │  Users   │         │   Application   │       │ (External)│  │
│  └──────────┘         └─────────────────┘       └──────────┘  │
│       ▲                       ▲                                 │
│       │                       │                                 │
│       ▼                       ▼                                 │
│  ┌──────────┐         ┌─────────────────┐                      │
│  │  Nurse/  │         │  HIPAA Training │                      │
│  │  Staff   │         │    Platform     │                      │
│  └──────────┘         └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  LEVEL 2: CONTAINER DIAGRAM                                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Web Browser (Client)                                      │ │
│  │  - React 18 Components                                     │ │
│  │  - Vanilla JavaScript                                      │ │
│  │  - HTML5 Templates (Jinja2)                                │ │
│  │  - Session Management (2-min timeout)                      │ │
│  └────────────────────┬───────────────────────────────────────┘ │
│                       │ HTTPS (required for production)         │
│                       │ HTTP (demo/localhost only)              │
│                       ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Flask Web Application Server                              │ │
│  │  - Flask 3.1.2 (Python 3.x)                                │ │
│  │  - RESTful API Endpoints (/api/*)                          │ │
│  │  - Session Management (server-side)                        │ │
│  │  - Authentication & Authorization (RBAC)                   │ │
│  │  - Business Logic Layer                                    │ │
│  │  - Flask-CORS (API access control)                         │ │
│  └────────────────────┬───────────────────────────────────────┘ │
│                       │                                          │
│                       ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Data Access Layer                                         │ │
│  │  - SQLite3 Database Driver                                 │ │
│  │  - Parameterized Queries (SQL injection prevention)       │ │
│  │  - Connection Management                                   │ │
│  └────────────────────┬───────────────────────────────────────┘ │
│                       │                                          │
│                       ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  SQLite Database (securemed.db)                            │ │
│  │  - users (credentials, roles)                              │ │
│  │  - patients (PHI with encrypted SSN)                       │ │
│  │  - audit_results (violations, findings)                    │ │
│  │  - activity_log (audit trail)                              │ │
│  │  - directory (approved PHI recipients)                     │ │
│  │  - assignments (staff tasks)                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  External Components                                        │ │
│  │  - Cryptography Library (Fernet AES-128)                   │ │
│  │  - ReportLab (PDF Generation)                              │ │
│  │  - Werkzeug (WSGI Utilities)                               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Component Descriptions

#### 1. Web Browser (Frontend)

**Technology Stack:**
- React 18 (loaded via CDN: https://unpkg.com/react@18/umd/react.production.min.js)
- React DOM 18
- Vanilla JavaScript (ES6+)
- HTML5 Templates (Jinja2 server-side rendering)
- CSS3 (inline and external stylesheets)

**Key Components:**
- `Dashboard Component` - Admin main dashboard with metrics
- `UserDashboard Component` - Nurse dashboard with compliance scorecard
- `PatientTable Component` - Patient list with CRUD operations
- `TrainingModule Component` - Interactive HIPAA training
- `EDRPanel Component` - Endpoint detection and response interface
- `AuditTrailTable Component` - Activity log viewer
- `DirectoryTable Component` - Approved PHI recipients

**State Management:**
- Local component state (React useState hooks)
- Session storage for user context
- LocalStorage for UI preferences (deprecated, moved to DB)

**Security Features:**
- Automatic session timeout (2 minutes)
- Activity detection (mouse, keyboard, scroll events)
- Warning modal before timeout (90 seconds)
- Automatic redirection to login on session expiry

#### 2. Flask Web Application

**Technology Stack:**
- Flask 3.1.2 (Python web framework)
- Werkzeug 3.1.3 (WSGI utilities)
- Jinja2 3.1.6 (template engine)
- Flask-CORS 6.0.1 (Cross-Origin Resource Sharing)

**Architecture Layers:**

**Presentation Layer:**
- Route handlers (`@app.route` decorators)
- Request/response processing
- Template rendering
- JSON API responses

**Business Logic Layer:**
- Authentication logic (login, password reset)
- Authorization logic (role-based access)
- HIPAA compliance scoring
- Violation tracking
- Training module management
- Breach simulation logic

**Data Access Layer:**
- Database connection management
- CRUD operations (Create, Read, Update, Delete)
- Parameterized SQL queries
- Transaction management

**Security Layer:**
- Session management (server-side)
- Password hashing (SHA-256)
- Encryption/decryption (Fernet wrapper)
- Audit logging (all actions)
- Input validation and sanitization

#### 3. Database Layer

**Database:** SQLite3 (file: `securemed.db`)

**Schema:**

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- SHA-256 hashed
    role TEXT NOT NULL,      -- 'admin' or 'user'
    first_name TEXT,
    last_name TEXT,
    dob TEXT,                -- For password reset verification
    ssn_last4 TEXT,          -- For password reset verification
    compliance_score REAL DEFAULT 0,
    completed_modules TEXT DEFAULT '[]',  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patients table
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mrn TEXT UNIQUE NOT NULL,          -- Medical Record Number
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    dob TEXT NOT NULL,
    ssn TEXT NOT NULL,                 -- ENCRYPTED with Fernet
    email TEXT,
    phone TEXT,
    address TEXT,
    created_by TEXT,                   -- Username of creator
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit results (violations, findings)
CREATE TABLE audit_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    violation_type TEXT NOT NULL,
    severity TEXT NOT NULL,            -- 'Critical', 'High', 'Medium', 'Low'
    description TEXT NOT NULL,
    hipaa_section TEXT,                -- e.g., '§164.312(b)'
    affected_system TEXT,
    nurse_username TEXT,               -- If individual violation
    resolved BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activity log (audit trail)
CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    action TEXT NOT NULL,              -- 'LOGIN', 'PATIENT_ACCESSED', etc.
    description TEXT,
    details TEXT,                      -- Additional context
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Directory (approved PHI recipients)
CREATE TABLE directory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_type TEXT NOT NULL,        -- 'fax', 'email', 'hospital', etc.
    contact_name TEXT NOT NULL,
    contact_info TEXT NOT NULL,        -- Phone, email, or address
    approved BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assignments (staff tasks)
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assigned_to TEXT NOT NULL,         -- Username
    assignment_type TEXT NOT NULL,     -- 'fax', 'email', 'transfer', etc.
    description TEXT NOT NULL,
    correct_answer TEXT NOT NULL,      -- Expected contact_info
    patient_mrn TEXT,                  -- Reference to patient
    completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
```sql
CREATE INDEX idx_activity_username ON activity_log(username);
CREATE INDEX idx_audit_nurse ON audit_results(nurse_username);
CREATE INDEX idx_patients_mrn ON patients(mrn);
```

### Data Flow Diagrams

#### Authentication Flow
```
User → Login Form → POST /login →
Flask validates credentials →
Query users table →
SHA-256 hash comparison →
Create session →
Log to activity_log →
Redirect to dashboard →
Return dashboard with user context
```

#### Patient Access Flow
```
Nurse → Click "View Patients" →
GET /api/patients →
Flask checks session & role →
Query patients table →
Decrypt SSN (Fernet) →
Log access to activity_log →
Return JSON patient list →
React renders table
```

#### Training Module Flow
```
Nurse → Complete quiz question →
POST /api/training/submit →
Flask validates answer →
If correct: update compliance_score →
If incorrect: create audit_result violation →
Update completed_modules →
Log to activity_log →
Return updated score →
React updates UI
```

### Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | React | 18.x | UI components |
| Frontend | Vanilla JS | ES6+ | Session timeout, DOM manipulation |
| Frontend | Jinja2 | 3.1.6 | Server-side template rendering |
| Backend | Flask | 3.1.2 | Web framework |
| Backend | Python | 3.8+ | Core language |
| Backend | Flask-CORS | 6.0.1 | API CORS handling |
| Database | SQLite3 | 3.x | Data persistence |
| Encryption | cryptography | 46.0.3 | Fernet AES-128 |
| PDF | ReportLab | 4.4.4 | Compliance report generation |
| WSGI | Werkzeug | 3.1.3 | Development server |

### Security Architecture

**Defense in Depth:**

1. **Network Layer** (not implemented in demo)
   - TLS/HTTPS encryption
   - Firewall rules
   - Rate limiting

2. **Application Layer** (✅ implemented)
   - Session management
   - Role-based access control
   - Input validation
   - SQL injection prevention (parameterized queries)
   - XSS prevention (Jinja2 auto-escaping)

3. **Data Layer** (✅ implemented)
   - Field-level encryption (SSN)
   - Password hashing (SHA-256)
   - Audit logging
   - Database file permissions

4. **Physical Layer** (demo/localhost)
   - File system access control
   - Secure key storage (hardcoded for demo)

---

## API Reference

### Base URL
```
Development: http://127.0.0.1:5000
Production: https://securemed.yourdomain.com
```

### Authentication

All API endpoints (except `/login` and `/reset_password`) require an active session cookie.

**Session Cookie:**
- Name: `session`
- HttpOnly: Yes
- Secure: No (demo), Yes (production with HTTPS)
- SameSite: Lax
- Max-Age: 120 seconds (2 minutes)

### Endpoints

#### Authentication Endpoints

##### POST /login
**Description:** Authenticate user and create session

**Request Body:**
```json
{
  "username": "admin",
  "password": "Admin123!"
}
```

**Response (Success):**
```json
{
  "message": "Login successful",
  "redirect": "/dashboard"
}
```

**Response (Failure):**
```json
{
  "error": "Invalid username or password"
}
```

**Status Codes:**
- `200 OK` - Login successful
- `401 Unauthorized` - Invalid credentials

**Audit Log:** Creates `LOGIN` activity log entry

---

##### POST /logout
**Description:** End user session

**Request:** No body required

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

**Audit Log:** Creates `LOGOUT` activity log entry

---

##### POST /reset_password
**Description:** Reset user password with DOB + SSN verification

**Request Body:**
```json
{
  "username": "stefan",
  "dob": "1990-05-15",
  "ssn_last4": "1234",
  "new_password": "NewSecure123!"
}
```

**Response (Success):**
```json
{
  "message": "Password reset successfully"
}
```

**Response (Failure):**
```json
{
  "error": "Invalid verification information"
}
```

**Validation:**
- DOB and SSN last 4 must match user record
- New password must meet complexity requirements

**Audit Log:** Creates `PASSWORD_RESET` activity log entry

---

#### Patient Management Endpoints

##### GET /api/patients
**Description:** Retrieve all patients (SSN decrypted for authorized users)

**Authentication:** Required
**Authorization:** Admin or User role

**Response:**
```json
[
  {
    "id": 1,
    "mrn": "MRN2871",
    "first_name": "John",
    "last_name": "Doe",
    "dob": "1985-03-15",
    "ssn": "***-**-6789",
    "email": "john.doe@email.com",
    "phone": "555-0101",
    "address": "123 Main St, City, ST 12345",
    "created_by": "admin",
    "created_at": "2024-11-15 10:30:00"
  }
]
```

**SSN Display:**
- Masked by default: `***-**-6789`
- Full SSN shown when user clicks "eye" icon (decrypted on-demand)

**Audit Log:** Creates `PATIENTS_ACCESSED` activity log entry

---

##### POST /api/add_patient
**Description:** Create new patient record

**Authentication:** Required
**Authorization:** Admin or User role

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "dob": "1992-07-20",
  "ssn": "123-45-6789",
  "email": "jane.smith@email.com",
  "phone": "555-0102",
  "address": "456 Oak Ave, City, ST 12345"
}
```

**Response (Success):**
```json
{
  "message": "Patient added successfully",
  "mrn": "MRN2872"
}
```

**Validation:**
- All fields required except email/phone/address
- SSN must be 9 digits (accepts XXX-XX-XXXX or XXXXXXXXX format)
- Auto-generates unique MRN
- Encrypts SSN before storage

**Audit Log:** Creates `PATIENT_ADDED` activity log entry

---

##### POST /api/edit_patient
**Description:** Update patient contact information

**Authentication:** Required
**Authorization:** Admin or User role

**Request Body:**
```json
{
  "patient_id": 1,
  "email": "updated.email@example.com",
  "phone": "555-9999",
  "address": "789 New St, City, ST 12345"
}
```

**Response (Success):**
```json
{
  "message": "Patient updated successfully"
}
```

**Editable Fields:**
- ✅ Email
- ✅ Phone
- ✅ Address

**Protected Fields (cannot edit):**
- ❌ MRN
- ❌ First Name / Last Name
- ❌ Date of Birth
- ❌ SSN

**Audit Log:** Creates `PATIENT_INFO_UPDATED` activity log entry with before/after values

---

##### DELETE /api/delete_patient/<patient_id>
**Description:** Delete patient record

**Authentication:** Required
**Authorization:** Admin only

**Response (Success):**
```json
{
  "message": "Patient deleted successfully"
}
```

**Audit Log:** Creates `PATIENT_DELETED` activity log entry

---

#### Training & Compliance Endpoints

##### POST /api/training/submit
**Description:** Submit training quiz answer and update compliance score

**Authentication:** Required
**Authorization:** User role

**Request Body:**
```json
{
  "module_id": "module1",
  "question_id": 1,
  "answer": "Correct answer text",
  "is_correct": true
}
```

**Response (Success):**
```json
{
  "message": "Answer recorded",
  "compliance_score": 66.67,
  "module_complete": true
}
```

**Logic:**
- If correct: increment module progress
- If incorrect: create `audit_result` violation
- Update `compliance_score` = (completed questions / 9 total) × 100
- Mark module complete when all 3 questions answered correctly

**Audit Log:** Creates `TRAINING_COMPLETED` or `TRAINING_VIOLATION` activity log entry

---

##### GET /api/compliance_score/<username>
**Description:** Retrieve user's HIPAA compliance score

**Authentication:** Required

**Response:**
```json
{
  "username": "stefan",
  "compliance_score": 100.0,
  "completed_modules": ["module1", "module2", "module3"]
}
```

---

#### Violations & Audit Endpoints

##### GET /api/violations
**Description:** Retrieve HIPAA violations

**Authentication:** Required
**Authorization:** Admin or User (scoped to own violations)

**Query Parameters:**
- `?role=admin` - Returns all organizational violations (admins only)
- `?role=user&username=stefan` - Returns individual violations for user

**Response:**
```json
[
  {
    "id": 1,
    "violation_type": "Training Failure",
    "severity": "Medium",
    "description": "Failed quiz question: Module 1, Question 2",
    "hipaa_section": "§164.308(a)(5)(i)",
    "affected_system": "Training Simulator",
    "nurse_username": "stefan",
    "resolved": false,
    "created_at": "2024-11-15 14:20:00"
  }
]
```

---

##### GET /api/activity_log
**Description:** Retrieve audit trail

**Authentication:** Required
**Authorization:** Admin only

**Response:**
```json
[
  {
    "id": 1,
    "username": "stefan",
    "action": "LOGIN",
    "description": "User logged in",
    "details": "",
    "ip_address": "127.0.0.1",
    "timestamp": "2024-11-15 10:00:00"
  }
]
```

**Action Types:**
- `LOGIN`, `LOGOUT`
- `PATIENT_ADDED`, `PATIENT_ACCESSED`, `PATIENT_INFO_UPDATED`, `PATIENT_DELETED`
- `TRAINING_COMPLETED`, `TRAINING_VIOLATION`
- `ASSIGNMENT_COMPLETED`
- `PASSWORD_RESET`
- `BREACH_SIMULATED`

---

#### Administration Endpoints

##### POST /api/simulate_breach
**Description:** Trigger breach simulation for EDR testing

**Authentication:** Required
**Authorization:** Admin only

**Request Body:**
```json
{
  "breach_type": "Ransomware Attack"
}
```

**Breach Types:**
- `Ransomware Attack`
- `Insider Data Theft`
- `Phishing Attack`
- `Database Exposed to Internet`
- `Laptop Theft (Unencrypted)`

**Response:**
```json
{
  "message": "Breach simulated successfully",
  "breach_id": 5
}
```

**Audit Log:** Creates `BREACH_SIMULATED` activity log entry

---

##### POST /api/quick_setup
**Description:** Generate demo data (patients, violations, assignments)

**Authentication:** Required
**Authorization:** Admin only

**Response:**
```json
{
  "message": "Demo data generated successfully",
  "patients_created": 5,
  "violations_created": 10,
  "assignments_created": 3
}
```

**Generated Data:**
- 5 sample patients
- 10 HIPAA violations (mix of organizational and individual)
- 3 task assignments
- EDR vulnerabilities

---

##### POST /api/demo_reset
**Description:** Full database reset (deletes all data except users)

**Authentication:** Required
**Authorization:** Admin only

**Response:**
```json
{
  "message": "Full demo reset completed"
}
```

**Data Deleted:**
- All patients
- All violations
- All assignments
- All activity logs
- User training progress (compliance scores reset to 0)

**Data Preserved:**
- User accounts and credentials
- Directory entries

---

##### GET /api/generate_report
**Description:** Generate PDF HIPAA compliance report

**Authentication:** Required
**Authorization:** Admin only

**Response:** PDF file download
**Content-Type:** `application/pdf`
**Filename:** `hipaa_compliance_report_YYYY-MM-DD.pdf`

**Report Contents:**
- Executive summary
- Violation list with severity
- HIPAA section mapping
- Remediation recommendations
- Signature section

---

### Error Responses

**Standard Error Format:**
```json
{
  "error": "Descriptive error message"
}
```

**Common Status Codes:**
- `200 OK` - Request successful
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error (logged)

---

## Deployment Guide

### Prerequisites

**System Requirements:**
- Python 3.8 or higher
- pip (Python package manager)
- 50 MB disk space
- 512 MB RAM minimum

**Supported Platforms:**
- macOS (tested on macOS 10.15+)
- Linux (Ubuntu 20.04+, CentOS 8+)
- Windows 10/11

### Local Development Setup

#### 1. Install Dependencies

```bash
# Navigate to project directory
cd /path/to/Cap_Finaldev

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Initialize Database

Database auto-initializes on first run. To manually reset:

```bash
# Delete existing database
rm securemed.db

# Run application (creates new database)
python webapp.py
```

#### 3. Run Application

```bash
# Development server (Flask built-in)
python webapp.py

# Application runs on: http://127.0.0.1:5000
```

#### 4. Access Application

Open browser to: **http://127.0.0.1:5000/login**

**Default Credentials:**
- Admin: `admin` / `Admin123!`
- User: `stefan` / `Stefan123!`

### Production Deployment

⚠️ **WARNING:** Current setup is for educational/demo purposes only. Production deployment requires significant security hardening.

#### Production Checklist

- [ ] Deploy with production WSGI server (Gunicorn/uWSGI, not Flask dev server)
- [ ] Enable HTTPS with valid SSL certificate (Let's Encrypt)
- [ ] Migrate to PostgreSQL or MySQL (not SQLite)
- [ ] Use environment variables for secrets (not hardcoded keys)
- [ ] Implement key management system (AWS KMS, HashiCorp Vault)
- [ ] Enable multi-factor authentication (MFA)
- [ ] Add rate limiting (Flask-Limiter)
- [ ] Implement CSRF protection (Flask-WTF)
- [ ] Set up log aggregation (ELK stack, Splunk)
- [ ] Deploy Web Application Firewall (WAF)
- [ ] Configure automated backups
- [ ] Set up monitoring and alerting

#### Example Production Deployment (Linux + Gunicorn + Nginx)

**1. Install Production Dependencies:**
```bash
pip install gunicorn psycopg2-binary python-dotenv
```

**2. Create Environment File (`.env`):**
```bash
FLASK_ENV=production
SECRET_KEY=generate-strong-random-key-here
ENCRYPTION_KEY=generate-fernet-key-here
DATABASE_URL=postgresql://user:pass@localhost/securemed
```

**3. Run with Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 webapp:app
```

**4. Configure Nginx Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name securemed.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name securemed.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/securemed.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/securemed.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**5. Set Up Systemd Service:**
```ini
[Unit]
Description=SecureMed Gunicorn Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/securemed
Environment="PATH=/var/www/securemed/venv/bin"
ExecStart=/var/www/securemed/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 webapp:app

[Install]
WantedBy=multi-user.target
```

### Operations Runbook

#### Daily Operations

**Monitoring:**
```bash
# Check application logs
tail -f /var/log/securemed/app.log

# Check Nginx logs
tail -f /var/log/nginx/access.log
```

**Database Backup:**
```bash
# SQLite backup (demo)
cp securemed.db backups/securemed_$(date +%Y%m%d).db

# PostgreSQL backup (production)
pg_dump securemed > backups/securemed_$(date +%Y%m%d).sql
```

#### Incident Response

**Suspected Breach:**
1. Immediately review activity logs: `SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 100;`
2. Check for suspicious login patterns (multiple failed attempts)
3. Review patient access logs for unauthorized access
4. Generate compliance report for incident documentation
5. Follow breach notification procedures (HIPAA 60-day requirement)

**System Down:**
1. Check Flask/Gunicorn process: `systemctl status securemed`
2. Check Nginx: `systemctl status nginx`
3. Review error logs: `tail -100 /var/log/securemed/error.log`
4. Restart services if needed: `systemctl restart securemed`

**Database Corruption:**
1. Stop application
2. Restore from latest backup
3. Verify data integrity
4. Restart application
5. Document incident in activity log

---

## Product Backlog

### Current Sprint (Sprint 4 - Completed)
**Sprint Goal:** Final testing, security audit, documentation

| ID | Priority | Story | Estimate | Status | Assignee |
|----|----------|-------|----------|--------|----------|
| S4-1 | High | As an admin, I need patient editing capability | 5 pts | ✅ Done | Stefan |
| S4-2 | High | As a developer, I need comprehensive testing | 8 pts | ✅ Done | Ana |
| S4-3 | Medium | As a user, I need updated compliance scoring | 3 pts | ✅ Done | Jordan |
| S4-4 | Medium | As an admin, I need accurate HIPAA reports | 5 pts | ✅ Done | Mumin |
| S4-5 | Low | As a user, I need faster SSN masking | 2 pts | ✅ Done | Stefan |

**Sprint 4 Velocity:** 23 story points completed

### Prioritized Backlog (Top 15 Future Enhancements)

| Rank | ID | Priority | User Story | Estimate | Business Value |
|------|------|----------|------------|----------|----------------|
| 1 | BP-1 | 🔴 Critical | As a security admin, I need HTTPS/TLS encryption for all traffic | 13 pts | Compliance requirement |
| 2 | BP-2 | 🔴 Critical | As a user, I need multi-factor authentication (MFA) for login | 8 pts | Enhanced security |
| 3 | BP-3 | 🔴 Critical | As a developer, I need environment-based configuration (not hardcoded keys) | 5 pts | Security best practice |
| 4 | BP-4 | 🔴 High | As an admin, I need rate limiting to prevent brute force attacks | 5 pts | Security hardening |
| 5 | BP-5 | 🔴 High | As a developer, I need CSRF protection on all forms | 3 pts | Security compliance |
| 6 | BP-6 | 🟡 High | As a DBA, I need PostgreSQL database migration | 13 pts | Production scalability |
| 7 | BP-7 | 🟡 Medium | As an admin, I need account lockout after 5 failed logins | 5 pts | Security policy |
| 8 | BP-8 | 🟡 Medium | As a compliance officer, I need encrypted audit logs | 8 pts | Enhanced audit security |
| 9 | BP-9 | 🟡 Medium | As a user, I need password expiration (90 days) | 5 pts | HIPAA best practice |
| 10 | BP-10 | 🟡 Medium | As an admin, I need real-time SIEM integration (Splunk/ELK) | 21 pts | Security monitoring |
| 11 | BP-11 | 🟢 Low | As a user, I need email notifications for training deadlines | 8 pts | User engagement |
| 12 | BP-12 | 🟢 Low | As an admin, I need automated vulnerability scanning (Snyk) | 13 pts | Proactive security |
| 13 | BP-13 | 🟢 Low | As a patient, I need a patient portal to view my records | 21 pts | Patient engagement |
| 14 | BP-14 | 🟢 Low | As a developer, I need API versioning (v1, v2) | 5 pts | Future-proofing |
| 15 | BP-15 | 🟢 Low | As a mobile user, I need responsive mobile design | 13 pts | User experience |

**Backlog Link:** [GitHub Projects Board](#) (create if open-sourcing)

### Definition of Done

A user story is considered "Done" when:
- [ ] Code implemented and peer-reviewed
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Security review completed (for sensitive features)
- [ ] Documentation updated
- [ ] Deployed to demo environment
- [ ] Acceptance criteria validated by Product Owner
- [ ] No critical bugs remaining

---

## Scrum Evidence

### Sprint Planning

#### Sprint 1: Foundation & Research (Weeks 1-2)
**Sprint Goal:** Establish architecture, research HIPAA requirements, set up development environment

**Planning Meeting Notes:**
- **Date:** October 1, 2024
- **Duration:** 2 hours
- **Attendees:** Stefan, Ana, Jordan, Jeremiah, Mumin

**Sprint Backlog:**

| Story ID | Story | Owner | Estimate | Actual |
|----------|-------|-------|----------|--------|
| S1-1 | Design database schema with encryption | Stefan | 8 pts | 9 pts |
| S1-2 | Research HIPAA Security Rule requirements | Ana | 5 pts | 5 pts |
| S1-3 | Create UI mockups and wireframes | Jordan | 5 pts | 6 pts |
| S1-4 | Research healthcare vulnerabilities | Jeremiah | 5 pts | 4 pts |
| S1-5 | Set up documentation structure | Mumin | 3 pts | 3 pts |

**Sprint 1 Velocity:** 26 story points (planned) / 27 story points (actual)

**Key Decisions:**
- Chose Flask over Django for simplicity
- Decided on SQLite for demo (PostgreSQL for production)
- Selected Fernet (AES-128) for encryption
- React via CDN (no build tooling for simplicity)

---

#### Sprint 2: Core Development (Weeks 3-4)
**Sprint Goal:** Build backend API, implement authentication, create initial frontend

**Planning Meeting Notes:**
- **Date:** October 15, 2024
- **Duration:** 1.5 hours
- **Attendees:** All team members

**Sprint Backlog:**

| Story ID | Story | Owner | Estimate | Actual |
|----------|-------|-------|----------|--------|
| S2-1 | Implement database with encryption | Stefan | 13 pts | 15 pts |
| S2-2 | Build secure Flask API endpoints | Ana | 8 pts | 10 pts |
| S2-3 | Create React + Tailwind prototype | Jordan | 13 pts | 12 pts |
| S2-4 | Demonstrate SQL injection vulnerability | Jeremiah | 3 pts | 3 pts |
| S2-5 | Build PDF generation prototype | Mumin | 8 pts | 9 pts |

**Sprint 2 Velocity:** 45 story points (planned) / 49 story points (actual)

**Challenges:**
- Encryption integration took longer than expected
- Jinja2 vs React rendering conflicts (resolved with hybrid approach)

---

#### Sprint 3: Integration & Expansion (Weeks 5-6)
**Sprint Goal:** Full-stack integration, security hardening, feature expansion

**Planning Meeting Notes:**
- **Date:** October 29, 2024
- **Duration:** 2 hours
- **Attendees:** All team members

**Sprint Backlog:**

| Story ID | Story | Owner | Estimate | Actual |
|----------|-------|-------|----------|--------|
| S3-1 | Integrate backend and frontend | Stefan | 13 pts | 14 pts |
| S3-2 | Implement JWT auth + HTTPS + penetration testing | Ana | 13 pts | 10 pts |
| S3-3 | Expand UI functionality (audit, edit forms) | Jordan | 8 pts | 9 pts |
| S3-4 | Build threat detection module | Jeremiah | 8 pts | 10 pts |
| S3-5 | Automate PDF report integration | Mumin | 5 pts | 6 pts |

**Sprint 3 Velocity:** 47 story points (planned) / 49 story points (actual)

**Retrospective Action Items:**
- Improve communication during integration (resolved with daily check-ins)
- Ana and Stefan pair programming sessions very effective

---

#### Sprint 4: Testing & Polish (Weeks 7-8)
**Sprint Goal:** Comprehensive testing, security audit, final documentation

**Planning Meeting Notes:**
- **Date:** November 12, 2024
- **Duration:** 1.5 hours
- **Attendees:** All team members

**Sprint Backlog:**

| Story ID | Story | Owner | Estimate | Actual |
|----------|-------|-------|----------|--------|
| S4-1 | Add patient editing capability | Stefan | 5 pts | 6 pts |
| S4-2 | Conduct comprehensive testing | Ana | 8 pts | 8 pts |
| S4-3 | Fix compliance scoring | Jordan | 3 pts | 3 pts |
| S4-4 | Finalize HIPAA report formatting | Mumin | 5 pts | 5 pts |
| S4-5 | Optimize SSN masking delay | Stefan | 2 pts | 1 pt |

**Sprint 4 Velocity:** 23 story points (planned) / 23 story points (actual)

**Sprint Review Outcomes:**
- All acceptance criteria met
- Demo ready for capstone presentation
- Security audit completed with documented findings

---

### Daily Scrum Summaries

**Format:** Asynchronous via Slack/Discord (team preference)

**Week 1 Example (November 4-8, 2024):**

**Monday, November 4:**
- Stefan: Working on patient edit modal. Blocked: need confirmation on which fields are editable.
- Ana: Continuing penetration testing. No blockers.
- Jordan: Styling patient table. No blockers.
- Jeremiah: Integrating EDR panel with violations API. No blockers.
- Mumin: Formatting PDF report signatures. No blockers.

**Tuesday, November 5:**
- Stefan: Completed patient edit modal. Today: wire up backend API.
- Ana: Found 3 medium-severity vulnerabilities. Today: documenting findings.
- Jordan: Patient table complete. Today: testing responsive design.
- Jeremiah: EDR panel integration complete. Today: add live breach alerts.
- Mumin: PDF signatures working. Today: add compliance score charts.

**Wednesday, November 6:**
- Stefan: Patient editing API working. Today: add audit logging for edits.
- Ana: Pen test report 80% complete. Today: finish and review with team.
- Jordan: Responsive design tested on mobile. Today: fix compliance scorecard layout.
- Jeremiah: Breach alerts working. Today: test all 5 breach types.
- Mumin: Charts added to PDF. Today: final formatting polish.

**Thursday, November 7:**
- Stefan: Audit logging for patient edits complete. Today: code review with Ana.
- Ana: Pen test report complete. Today: conduct final security review.
- Jordan: Scorecard fixed. Today: prepare for sprint demo.
- Jeremiah: All breach types tested. Today: create demo script.
- Mumin: PDF formatting finalized. Today: generate sample reports for demo.

**Friday, November 8:**
- Stefan: Code review complete, all changes merged. Today: prepare demo environment.
- Ana: Security review complete. Today: document production hardening plan.
- Jordan: Sprint demo prep complete. Today: final UI testing.
- Jeremiah: Demo script ready. Today: practice breach simulation flow.
- Mumin: Sample reports generated. Today: finalize documentation.

---

### Sprint Reviews

#### Sprint 4 Review (November 15, 2024)
**Attendees:** All team members + faculty advisor

**Demonstrated Features:**
1. **Patient Editing** - Stefan demonstrated CRUD operations with audit logging
2. **Security Testing** - Ana presented penetration test results and findings
3. **UI Polish** - Jordan showcased responsive design and accessibility improvements
4. **EDR Panel** - Jeremiah simulated 5 breach types with incident response playbooks
5. **HIPAA Reports** - Mumin generated live PDF compliance report

**Acceptance Criteria Review:**
- ✅ All Sprint 4 stories met Definition of Done
- ✅ 34 unit/integration tests passing
- ✅ Security audit completed with no critical open issues
- ✅ Documentation complete and up-to-date
- ✅ Demo environment ready for capstone presentation

**Stakeholder Feedback:**
- "Impressed with security focus and HIPAA compliance depth"
- "Patient editing with protected fields is a nice touch"
- "Audit trail logging exceeds expectations"
- "PDF reports are professional quality"

**Product Backlog Refinement:**
- Prioritized HTTPS/MFA for future production deployment
- Discussed PostgreSQL migration timeline
- Agreed on SIEM integration as stretch goal

---

### Sprint Retrospectives

#### Sprint 1 Retrospective (October 14, 2024)

**What Went Well:**
- ✅ Clear role assignments based on team strengths
- ✅ Database schema design exceeded expectations
- ✅ Strong research foundation for HIPAA compliance
- ✅ Good communication and collaboration

**What Could Improve:**
- ⚠️ Initial estimates were too optimistic (improved in Sprint 2)
- ⚠️ Need more frequent check-ins during research phase

**Action Items:**
1. Hold mid-sprint check-in on day 5 of each sprint
2. Create shared knowledge base for HIPAA research findings
3. Schedule pair programming sessions for complex integrations

**Action Item Status (Sprint 2):** ✅ All implemented

---

#### Sprint 2 Retrospective (October 28, 2024)

**What Went Well:**
- ✅ Pair programming between Stefan and Ana very effective
- ✅ React prototype exceeded expectations
- ✅ Good progress on backend API
- ✅ Mid-sprint check-in improved team alignment

**What Could Improve:**
- ⚠️ Jinja2 vs React rendering conflicts caused delays
- ⚠️ Need clearer API contract before frontend work begins

**Action Items:**
1. Define API contracts before sprint starts (OpenAPI spec)
2. Create integration testing checklist
3. Schedule demo practice session before Sprint Review

**Action Item Status (Sprint 3):** ✅ All implemented

---

#### Sprint 3 Retrospective (November 11, 2024)

**What Went Well:**
- ✅ Full-stack integration smoother than expected
- ✅ Threat detection module very impressive
- ✅ Team velocity increasing (47 → 49 points)
- ✅ Demo practice session helped identify UI bugs early

**What Could Improve:**
- ⚠️ Need more automated tests (addressed in Sprint 4)
- ⚠️ Documentation lagging behind code

**Action Items:**
1. Write tests concurrently with features (TDD approach)
2. Update documentation immediately after feature completion
3. Create demo reset script for easier testing

**Action Item Status (Sprint 4):** ✅ All implemented

---

#### Sprint 4 Retrospective (November 16, 2024 - Final)

**What Went Well:**
- ✅ Comprehensive testing caught several edge cases
- ✅ Security audit revealed no critical issues
- ✅ Documentation is now complete and professional
- ✅ Team velocity consistent and predictable
- ✅ Demo environment rock-solid

**What Could Improve:**
- ⚠️ Earlier focus on testing would have saved time
- ⚠️ Production deployment plan should have started earlier

**Lessons Learned (Project-Wide):**
1. Security should be designed in from day 1, not added later
2. Pair programming significantly improves code quality
3. Regular demos and stakeholder feedback are invaluable
4. HIPAA compliance is complex but manageable with research
5. Team collaboration and communication are critical to success

**Team Shout-Outs:**
- Stefan: Exceptional database design and integration skills
- Ana: Security expertise brought professionalism to the project
- Jordan: UI/UX design made the application intuitive and beautiful
- Jeremiah: Cybersecurity knowledge added real-world credibility
- Mumin: Documentation and reports are capstone-quality

---

## Team Contributions

### Individual Contribution Summary

| Team Member | Primary Role | Hours | Key Deliverables | Lines of Code |
|-------------|-------------|-------|------------------|---------------|
| Stefan Dumitrasku | Backend Lead | 120 | Database, encryption, API integration | ~1,200 |
| Ana Salazar | Security Engineer | 120 | Authentication, security audit, pen testing | ~800 |
| Jordan Burgos | Frontend Developer | 120 | React components, UI/UX, responsive design | ~900 |
| Jeremiah Luzincourt | Cybersecurity Analyst | 120 | EDR panel, threat detection, vulnerability scanner | ~600 |
| Mumin Tahir | Documentation Lead | 120 | PDF generation, documentation, user guides | ~500 + 130 pages docs |
| **TOTAL** | **5 Members** | **600 hrs** | **Production-ready application** | **~4,000 LOC** |

### Detailed Contributions

See [docs/TEAM_CONTRIBUTIONS.md](docs/TEAM_CONTRIBUTIONS.md) for complete breakdown of individual contributions by sprint.

---

**Document Status:** Final
**Approval:** Team consensus (November 16, 2024)
**Next Review:** Post-submission (if productionized)
