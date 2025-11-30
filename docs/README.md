# SecureMed - Healthcare Cybersecurity & HIPAA Compliance Platform

A comprehensive healthcare security and compliance management system demonstrating HIPAA compliance requirements, security monitoring, and staff training.

## Team Members
- **Stefan Dumitrasku** - Project Lead & Backend Developer
- **Ana Salazar** - Security Analyst & Authentication Specialist
- **Jordan Burgos** - Frontend Developer & UI/UX Designer
- **Jeremiah Luzincourt** - Cybersecurity Analyst & EDR Developer
- **Mumin Tahir** - Documentation Lead & Report Generation Specialist

---

## Quick Start

### Installation (5 minutes)

```bash
# 1. Navigate to project directory
cd Cap_Finaldev

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run application
python webapp.py

# 6. Open browser to: http://127.0.0.1:5000/login
```

### Default Login Credentials

**Admin Account:**
- Username: `admin`
- Password: `Admin123!`

**Nurse/Staff Accounts:**
- Stefan: `stefan` / `Stefan123!`
- Ana: `ana` / `Ana123!`
- Jordan: `jordan` / `Jordan123!`
- Jeremiah: `jeremiah` / `Jeremiah123!`
- Mumin: `mumin` / `Mumin123!`

---

## Project Overview

SecureMed is a Flask-based web application simulating a healthcare organization's security infrastructure, providing hands-on experience with real-world HIPAA compliance, threat detection, and incident response capabilities.

### Core Features

**Security & Compliance:**
- 🔐 **Patient Management** - Encrypted PHI with AES-128 (Fernet)
- 🛡️ **EDR Panel** - Endpoint Detection & Response with breach simulation
- 📚 **HIPAA Training** - 3 interactive modules with compliance scoring
- 📊 **Audit Trail** - 100% coverage of PHI access events
- 📋 **Compliance Reports** - Automated PDF generation
- 🚨 **Breach Response** - 5 incident response playbooks
- 👥 **RBAC** - Role-based access control (Admin/User)

**Technical Highlights:**
- Flask 3.1.2 backend with React 18 frontend
- SQLite database with field-level encryption
- SHA-256 password hashing with complexity requirements
- Parameterized SQL queries (injection prevention)
- Automatic session timeout (2 minutes)
- Comprehensive activity logging

---

## 📚 Documentation

SecureMed includes comprehensive documentation organized into focused files:

### Essential Documentation

1. **[SECURITY.md](SECURITY.md)** - Complete security documentation
   - STRIDE threat model (27 threats analyzed)
   - Security controls & assurance mapping (HIPAA, NIST, OWASP)
   - Vulnerability assessment & penetration testing
   - SAST/DAST results
   - SBOM (Software Bill of Materials)
   - Remediation log

2. **[PROJECT.md](PROJECT.md)** - Project & technical documentation
   - System architecture (C4 container diagram)
   - Complete API reference (20+ endpoints)
   - Deployment guide (local & production)
   - Product backlog (prioritized top 15 items)
   - Scrum evidence (sprint planning, dailies, reviews, retros)
   - Team contributions breakdown

3. **[COMPLIANCE.md](COMPLIANCE.md)** - Compliance & ethics documentation
   - Executive summary (≤300 words)
   - HIPAA compliance statement (80% coverage)
   - Privacy & ethical impact assessment
   - Accessibility compliance (WCAG 2.1)
   - Demo video links & scripts
   - Regulatory compliance summary

4. **[sbom.json](sbom.json)** - Software Bill of Materials
   - CycloneDX format
   - 14 dependencies with licenses
   - Version tracking

### Additional Resources

- **[docs/INSTALL.md](docs/INSTALL.md)** - Detailed installation guide
- **[docs/HOW_TO_USE.md](docs/HOW_TO_USE.md)** - Step-by-step user guide
- **[docs/FEATURES.md](docs/FEATURES.md)** - Comprehensive feature documentation
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues & solutions
- **[docs/TESTING.md](docs/TESTING.md)** - Test documentation (34 tests)
- **[docs/TEAM_CONTRIBUTIONS.md](docs/TEAM_CONTRIBUTIONS.md)** - Individual contributions

---

## Key Features Deep Dive

### 1. Patient Management
- Add, view, edit, and delete patient records
- **Encrypted SSN** using Fernet (AES-128)
- Auto-generated Medical Record Numbers (MRN)
- Editable contact info (email, phone, address)
- Protected fields (MRN, name, DOB, SSN) - immutable
- All changes logged to audit trail

### 2. Security Monitoring (EDR Panel)
- Real-time threat detection with 5+ vulnerability types
- Active breach incident alerts (color-coded severity)
- System hardening status (5 security controls)
- **5 Breach Simulation Types:**
  - Ransomware Attack (20-step playbook)
  - Insider Data Theft (24 steps)
  - Phishing Attack (23 steps)
  - Database Exposure (23 steps)
  - Laptop Theft Unencrypted (25 steps)

### 3. HIPAA Training Simulator
- **3 Interactive Modules:**
  - Module 1: PHI Protection & Privacy
  - Module 2: Secure Communication
  - Module 3: Breach Prevention & Response
- Real-time compliance scoring (0-100%)
- Automatic violation logging for incorrect answers
- Training progress persisted in database

### 4. Audit Trail (HIPAA §164.312(b))
- **Complete activity logging:**
  - Login/logout tracking
  - Patient record access
  - Data modifications (before/after values)
  - Training completion
  - Password resets
  - Breach simulations
- IP address tracking
- Timestamp precision

### 5. Compliance Reporting
- Automated PDF report generation
- Violation severity breakdown
- HIPAA section mapping (§164.308-312)
- Remediation recommendations
- Signature sections

### 6. Task Assignment System
- Directory-based secure communication
- Minimum necessary principle enforcement
- 25+ approved contact locations
- Violation tracking for incorrect selections
- Case-insensitive validation

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend | Flask | 3.1.2 | Web framework |
| Backend | Python | 3.8+ | Core language |
| Frontend | React | 18.x | UI components |
| Frontend | Vanilla JS | ES6+ | Session management |
| Database | SQLite3 | 3.x | Data persistence |
| Encryption | cryptography | 46.0.3 | Fernet AES-128 |
| PDF | ReportLab | 4.4.4 | Report generation |
| CORS | Flask-CORS | 6.0.1 | API access control |

**Dependencies:** See [sbom.json](sbom.json) for complete list with licenses.

---

## HIPAA Compliance

SecureMed demonstrates **80% coverage** of HIPAA Security Rule requirements:

### Administrative Safeguards (§164.308)
- ✅ Risk Analysis & Management
- ✅ Security Officer Designation
- ✅ Workforce Security (RBAC)
- ✅ Access Management
- ✅ Security Awareness Training
- ✅ Sanction Policy (violation tracking)

### Physical Safeguards (§164.310)
- ✅ Workstation Security (session timeout)
- ⚠️ Facility Access Controls (demo environment)

### Technical Safeguards (§164.312)
- ✅ Unique User Identification
- ✅ Automatic Logoff (2-min timeout)
- ✅ Encryption/Decryption (AES-128)
- ✅ Audit Controls (100% logging)
- ✅ Integrity Controls (parameterized queries)
- ✅ Authentication (SHA-256 + password complexity)
- ❌ Transmission Security (no HTTPS in demo)

**Detailed Compliance Analysis:** See [COMPLIANCE.md](COMPLIANCE.md#hipaa-compliance-statement)

---

## Project Structure

```
Cap_Finaldev/
├── README.md                    # This file - project overview
├── SECURITY.md                  # Security & threat documentation
├── PROJECT.md                   # Architecture, API, Scrum evidence
├── COMPLIANCE.md                # HIPAA, privacy, accessibility
├── sbom.json                    # Software Bill of Materials
├── webapp.py                    # Main Flask application (800+ lines)
├── generate_report.py           # PDF report generation
├── encrypt_data.py              # Encryption utilities
├── test_webapp.py               # Test suite (34 tests)
├── requirements.txt             # Python dependencies
├── securemed.db                 # SQLite database (auto-generated)
├── templates/                   # HTML templates
│   ├── login.html
│   ├── dashboard_react.html    # Admin dashboard
│   ├── user_dashboard_react.html  # Nurse dashboard
│   ├── edr.html                # EDR panel
│   ├── training_simulator.html
│   ├── patients.html
│   ├── audit_trail.html
│   └── ...
├── docs/                        # Additional documentation
│   ├── INSTALL.md
│   ├── HOW_TO_USE.md
│   ├── FEATURES.md
│   ├── TROUBLESHOOTING.md
│   ├── TESTING.md
│   └── TEAM_CONTRIBUTIONS.md
└── seed_*.py                    # Database seeding scripts
```

---

## Demo Workflow

### 5-Minute Quick Demo
1. Login as admin (`admin` / `Admin123!`)
2. Click "⚡ Quick Setup" - generates demo data
3. Click "🚨 Simulate Breach" - choose Ransomware
4. View EDR Panel - see alerts and response playbook
5. Generate HIPAA Report - PDF downloads

### 10-Minute Complete Demo
1. Admin: Setup + breach simulation (3 min)
2. Logout, login as nurse (`stefan` / `Stefan123!`) (1 min)
3. Complete training module quiz (3 min)
4. View updated compliance score (1 min)
5. Admin reviews violations in EDR Panel (2 min)

**Detailed Demo Script:** See [COMPLIANCE.md](COMPLIANCE.md#demo-videos)

---

## Testing

### Run Test Suite

```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux

# Run all 34 tests
python test_webapp.py

# Expected output:
# Ran 34 tests in 2.3s
# OK
```

### Test Coverage
- 14 unit tests (password validation, encryption, database operations)
- 20 integration tests (API endpoints, authentication, RBAC)
- Security tests (SQL injection prevention, XSS, CSRF awareness)
- Performance benchmarks

**Detailed Testing Documentation:** See [docs/TESTING.md](docs/TESTING.md)

---

## Security Features

### Implemented (Demo-Ready)
- ✅ **Encryption at Rest:** AES-128 (Fernet) for SSN
- ✅ **Password Hashing:** SHA-256 one-way
- ✅ **Password Complexity:** 8+ chars, mixed case, numbers, special
- ✅ **Session Management:** 2-min timeout with activity tracking
- ✅ **Audit Logging:** All actions logged with timestamps, IP, user
- ✅ **RBAC:** Admin vs User permissions
- ✅ **SQL Injection Prevention:** Parameterized queries
- ✅ **XSS Prevention:** Jinja2 auto-escaping
- ✅ **Input Validation:** Server-side validation

### Required for Production
- ❌ **HTTPS/TLS:** No encryption in transit (HTTP only)
- ❌ **MFA:** No multi-factor authentication
- ❌ **Rate Limiting:** No brute force protection
- ❌ **CSRF Protection:** No CSRF tokens
- ❌ **Key Management:** Hardcoded encryption key
- ❌ **Production DB:** SQLite not suitable for scale

**Complete Security Analysis:** See [SECURITY.md](SECURITY.md)

---

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'flask'"**
```bash
# Solution: Activate venv and install dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**"TemplateNotFound: login.html"**
```bash
# Solution: Run from project root directory
cd Cap_Finaldev
python webapp.py
```

**Port Already in Use (macOS/Linux)**
```bash
lsof -ti:5000 | xargs kill -9
```

**Port Already in Use (Windows)**
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**More Solutions:** See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Deployment Notes

### Current Status: Educational/Demo
⚠️ **WARNING:** This application is for **educational purposes only**. Do not use with real patient data.

### Production Requirements
For real healthcare deployment, you must:
1. Deploy with production WSGI server (Gunicorn/uWSGI, not Flask dev server)
2. Enable HTTPS with valid SSL certificate (Let's Encrypt)
3. Migrate to PostgreSQL or MySQL (not SQLite)
4. Use environment variables for secrets (not hardcoded keys)
5. Implement key management system (AWS KMS, HashiCorp Vault)
6. Enable multi-factor authentication (MFA)
7. Add rate limiting (Flask-Limiter)
8. Implement CSRF protection (Flask-WTF)
9. Set up log aggregation (ELK stack, Splunk)
10. Deploy Web Application Firewall (WAF)

**Complete Deployment Guide:** See [PROJECT.md](PROJECT.md#deployment-guide)

**Production Hardening Roadmap:** See [SECURITY.md](SECURITY.md#remediation-log)

---

## License

**Educational/Academic Use Only**

This project was created for educational purposes as a capstone demonstration. It is not licensed for commercial use or deployment in actual healthcare environments without:
- Professional security audit
- HIPAA Business Associate Agreement
- Production security hardening
- Legal compliance review

---

## Acknowledgments

**HIPAA Guidance:**
- U.S. Department of Health & Human Services (HHS)
- HIPAA Security Rule documentation (45 CFR §164.308-312)
- NIST Cybersecurity Framework
- OWASP Top 10 Web Application Security

**Open Source Libraries:**
- Flask framework and community
- ReportLab PDF library
- Cryptography library maintainers
- React team

**Educational Support:**
- Capstone project advisors
- Cybersecurity program faculty

---

## Project Statistics

- **Development Time:** 8 weeks (4 sprints × 2 weeks)
- **Team Size:** 5 members
- **Total Effort:** 600 hours (5 × 15 hrs/week × 8 weeks)
- **Lines of Code:** ~4,000 (Python + JavaScript + HTML/CSS)
- **Test Coverage:** 34 tests (unit + integration)
- **Documentation Pages:** 130+ pages
- **HIPAA Compliance:** 80% Security Rule coverage
- **Sprint Velocity:** Average 36 story points per sprint

---

## Contact & Support

**Project Lead:** Stefan Dumitrasku
**Security Analyst:** Ana Salazar

**For Questions:**
1. Review [docs/HOW_TO_USE.md](docs/HOW_TO_USE.md)
2. Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. Review [docs/CAPSTONE_QA.md](docs/CAPSTONE_QA.md) for common questions

---

## Documentation Index

| Document | Description | Lines |
|----------|-------------|-------|
| [README.md](README.md) | This file - project overview & quick start | 350 |
| [SECURITY.md](SECURITY.md) | Threat model, controls, pen test, SBOM | 900 |
| [PROJECT.md](PROJECT.md) | Architecture, API, deployment, scrum evidence | 1,100 |
| [COMPLIANCE.md](COMPLIANCE.md) | Executive summary, HIPAA, privacy, accessibility | 800 |
| [sbom.json](sbom.json) | Software Bill of Materials (CycloneDX) | 90 |
| **Total Core Docs** | **5 files** | **~3,240 lines** |

**Additional Documentation:** See [docs/](docs/) folder for user guides, installation instructions, testing docs, and team contributions.

---

⚠️ **IMPORTANT:** This application is for educational purposes only. It demonstrates HIPAA compliance concepts but should not be used to store real patient data or in actual healthcare environments without proper security hardening and legal review.

**Version:** 1.0.0
**Last Updated:** November 25, 2024
**Capstone Project** - Healthcare Cybersecurity & HIPAA Compliance
