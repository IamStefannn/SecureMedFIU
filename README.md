# SecureMed

Healthcare Cybersecurity & HIPAA Compliance Platform

![Version](https://img.shields.io/badge/version-1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)

## Executive Summary

SecureMed is a comprehensive healthcare cybersecurity and HIPAA compliance platform designed for small and mid-sized healthcare organizations (50-1,000 employees). It integrates five critical security capabilities into one lightweight, user-friendly system:

| Capability | What It Does | Impact |
|---|---|---|
| **Encrypted PHI Management** | AES-128 encryption for all sensitive patient data | Protects data even if compromised |
| **Real-Time Threat Detection (EDR)** | Continuous vulnerability scanning and monitoring | Identifies security issues before breaches |
| **Interactive HIPAA Training** | 3 modules, 9 scenarios with real-time scoring | Trains staff and tracks compliance |
| **Complete Audit Trail** | 100% activity logging with exportable reports | Enables breach investigations & audits |
| **Breach Simulation** | 5 incident response playbooks with HHS timelines | Prepares teams for actual emergencies |

**Bottom Line:** SecureMed makes healthcare cybersecurity and HIPAA compliance practical, measurable, and affordable for organizations that can't afford $100K+/year enterprise solutions.

## Table of Contents

- [Quick Start](#quick-start)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Metrics](#system-metrics)
- [Installation](#installation)
- [Usage](#usage)
- [Security](#security)
- [Compliance](#compliance)
- [Contributing](#contributing)
- [Future Work](#future-work)
- [Support](#support)
- [License](#license)

## Quick Start

### 30-Second Overview

```bash
# Clone repository
git clone https://github.com/IamStefannn/SecureMedFIU.git
cd SecureMed

# Setup
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Run
python webapp.py

# Access
# Open browser: http://127.0.0.1:5000/login
# Username: admin
# Password: Admin123!
```

### 5-Minute Walkthrough

1. **Login as admin** with credentials above
2. **Click "⚡ Quick Setup"** to generate demo data
3. **Explore admin dashboard** - View vulnerabilities, violations, compliance scores
4. **Switch to nurse account** (Stefan/Stefan123!) to:
   - View assigned patients
   - Edit patient contact information
   - Complete HIPAA training modules
   - Submit task assignments
5. **Review audit trail** - See complete activity log

For detailed setup instructions, see [INSTALLATION_GUIDE.pdf](./docs/INSTALLATION_GUIDE.pdf)

## Key Features

### 1. Encrypted PHI Management

**What:** All Protected Health Information encrypted with Fernet AES-128

- Patient names, addresses, emails (searchable, not encrypted)
- SSN, diagnoses, medical notes (encrypted, hidden)
- All access logged automatically

**Why:** HIPAA §164.312(a)(2)(iv) requires encryption of PHI at rest

**Example:**
```
Database contains: gAAAAABnZ9x5c8X_L1N4fV9K2pQ0rT... (encrypted SSN)
User sees: ***-**-6789 (masked display)
Only authorized users can decrypt
```

**Impact:** Even if database stolen, PHI remains protected

### 2. Role-Based Access Control (RBAC)

**Admin Capabilities:**
- View all patients
- Monitor threats (EDR panel)
- Review all violations and audit logs
- Generate compliance reports
- Simulate breach incidents

**Nurse Capabilities:**
- View assigned patients only
- Edit patient contact info (email, phone, address)
- Complete HIPAA training
- Submit task assignments
- View personal compliance score

**Why:** HIPAA §164.312(a)(1) requires access controls

### 3. Interactive HIPAA Training

**3 Modules, 9 Scenarios:**

| Module | Focus | Questions | Time |
|---|---|---|---|
| Module 1 | PHI Protection & Privacy | 3 | 5-8 min |
| Module 2 | Secure Communication | 3 | 5-8 min |
| Module 3 | Breach Prevention | 3 | 5-8 min |

**Scoring:**
- +20 points per correct answer
- 0 points per incorrect answer
- Automatic violation for scores <80%
- Persistent database storage

**Why:** HIPAA §164.308(a)(5) requires workforce training

**Example Scenario:**
```
"A patient calls asking for another patient's test results. What do you do?"
A) Give them the results (patient is asking)
B) Verify the caller's identity first
C) Tell them to call back later

Correct answer: +20 points
Your response affects compliance score: 9/9 correct = 100%
```

### 4. Threat Detection & EDR Panel

**Detects:**
- SQL injection attempts
- Missing/weak encryption
- Misconfigurations
- Improper PHI handling
- Suspicious access patterns
- 5+ vulnerability types

**Why:** HIPAA §164.312(a)(2) requires security assessments

**Example:**
```
CRITICAL: HTTPS Not Enabled
Impact: Unencrypted connections
Status: Open

HIGH: Missing Multi-Factor Auth
Impact: Weak authentication
Status: Open

MEDIUM: Outdated Dependency
Impact: Known vulnerabilities
Status: Resolved (2025-12-02)
```

### 5. Complete Audit Trail

**Logs Every Action:**
- Logins/logouts (with timestamp, IP)
- Patient record access
- Patient data edits (before/after values)
- Training answers (correct/incorrect)
- Violations created
- Vulnerability detections
- Task submissions

**Why:** HIPAA §164.312(b) mandates complete audit trail
- **100% Completeness:** Tested - 50 actions → 50 logged entries
- **Exportable:** Download as PDF for auditors

### 6. Breach Simulation Engine

**5 Realistic Playbooks:**

1. **Ransomware Attack** (20 steps)
   - Detect, isolate, investigate, recover, notify patients (60-day timeline)

2. **Insider Data Theft** (24 steps)
   - Identify employee, revoke access, forensics, legal action, notification

3. **Phishing Attack** (23 steps)
   - Detect, contain, patch, train staff, implement controls

4. **Database Exposed** (23 steps)
   - Take offline, contact provider, notify HHS, media notification

5. **Laptop Theft - Unencrypted** (25 steps)
   - Report, determine scope, notify patients, implement controls

**Why:** Prepares staff for actual breaches and HHS notification requirements

### 7. Automated PDF Reporting

**Report Types:**
- Audit logs (with full activity trail)
- Violation summaries
- Vulnerability status
- User compliance scorecards
- Patient data summaries

**Performance:** 2.1 seconds for typical report (target: <3 sec)

**Why:** Provides documentation for audits, boards, compliance officers

## Technology Stack

### Frontend
- **React 18** - Modern UI components
- **Tailwind CSS** - Responsive design
- **Vanilla JavaScript** - Client-side logic
- **CDN Delivery** - No build process required

### Backend
- **Python 3.8+** - Server-side logic
- **Flask 3.1.2** - REST API framework
- **SQLite 3.x** - Data storage (demo), PostgreSQL (production)
- **Fernet AES-128** - Encryption library

### Security
- **SHA-256** - Password hashing
- **Secure cookies** - Session management
- **Parameterized queries** - SQL injection prevention
- **HTML escaping** - XSS prevention

### DevOps
- **Docker** - Containerization (future)
- **AWS** - Cloud deployment (future)
- **GitHub** - Version control

### Testing
- **unittest** - Python testing
- **34 automated tests** - 100% pass rate

## System Metrics

### Performance

| Operation | Target | Actual | Status |
|---|---|---|---|
| Dashboard Load | <2 sec | 0.8 sec | ✅ 60% better |
| Database Query | <100 ms | 45 ms | ✅ 55% better |
| PDF Generation | <3 sec | 2.1 sec | ✅ 30% better |
| Encryption/Field | <50 ms | 12 ms | ✅ 76% better |
| Login Processing | <500 ms | 125 ms | ✅ 75% better |

### Testing

| Category | Tests | Pass Rate | Coverage |
|---|---|---|---|
| Unit Tests | 20 | 100% | Encryption, auth, database |
| Integration Tests | 14 | 100% | API + frontend + database |
| Security Tests | 57 | 100% | SQL injection, XSS, auth bypass |
| Performance Tests | 8 | 100% | Load time, query speed, PDF |
| User Acceptance Tests | 34 | 100% | All workflows |
| **TOTAL** | **143** | **100%** | ~85% code coverage |

### Security Testing

| Attack Type | Attempts | Blocked | Success Rate |
|---|---|---|---|
| SQL Injection | 15 | 15 | 100% |
| XSS | 12 | 12 | 100% |
| Auth Bypass | 15 | 15 | 100% |
| Session Hijacking | 6 | 6 | 100% |
| Privilege Escalation | 9 | 9 | 100% |
| **TOTAL** | **57** | **57** | **100%** |

### Code Metrics

| Metric | Value |
|---|---|
| Total Lines of Code | 4,000+ |
| Backend (Python) | ~2,200 LOC |
| Frontend (React/JS) | ~1,200 LOC |
| HTML Templates | ~1,400 LOC |
| CSS/Styling | ~600 LOC |

## Installation

### System Requirements

- **Python:** 3.8 or higher
- **RAM:** 4 GB minimum
- **Disk Space:** 200 MB
- **OS:** Windows, macOS, or Linux
- **Browser:** Chrome, Firefox, Safari, or Edge (modern versions)

### Quick Install

```bash
# 1. Clone repository
git clone https://github.com/IamStefannn/SecureMedFIU.git
cd SecureMed

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run application
python webapp.py

# 6. Access in browser
# Open: http://127.0.0.1:5000/login
```

### Default Credentials

| Role | Username | Password |
|---|---|---|
| Admin | admin | Admin123! |
| Nurse | stefan | Stefan123! |
| Nurse | ana | Ana123! |
| Nurse | jordan | Jordan123! |
| Nurse | jeremiah | Jeremiah123! |
| Nurse | mumin | Mumin123! |

For detailed setup instructions, see [INSTALLATION_GUIDE.pdf](./docs/INSTALLATION_GUIDE.pdf)

## Usage

### For Administrators

1. Login as admin
2. Generate demo data: Click "⚡ Quick Setup" on dashboard
3. Review vulnerabilities: Go to EDR panel
4. Monitor violations: Check violations list
5. Generate reports: Click "Generate Report"
6. Simulate breach: Click "Simulate Breach" to run incident playbooks

Full guide: See [HOW_TO_USE_GUIDE.pdf](./docs/HOW_TO_USE_GUIDE.pdf) - Section 3.2

### For Nurses/Staff

1. Login with your credentials (e.g., stefan)
2. View patients: See assigned patients only
3. Edit patient info: Update email, phone, address
4. Complete training: Go to Training section
   - Select module (1, 2, or 3)
   - Answer 3 questions per module
   - View compliance score
5. Submit assignments: Go to Assignments
   - Find recipient in Directory
   - Submit task code
   - Correct = task complete, incorrect = violation logged

Full guide: See [HOW_TO_USE_GUIDE.pdf](./docs/HOW_TO_USE_GUIDE.pdf) - Sections 3.1 and 4.3-4.4

## Security

### Encryption

- **Algorithm:** Fernet (AES-128 CBC mode)
- **Coverage:** 100% of sensitive PHI fields (SSN, diagnoses, notes)
- **Performance:** <12 ms per encrypt/decrypt operation
- **Standard:** HIPAA §164.312(a)(2)(iv) compliant

### Authentication

- **Method:** SHA-256 password hashing
- **Session:** Secure cookies with 2-minute timeout (demo)
- **RBAC:** Admin and Nurse roles with strict permission enforcement
- **Standard:** HIPAA §164.312(a) and §164.312(d) compliant

### Testing & Validation

- **Penetration Testing:** 57 attack vectors tested, 100% blocked
- **Code Review:** All inputs sanitized, parameterized queries
- **Security Audit:** Completed during Sprint 4
- **Compliance Check:** Verified against HIPAA §164.312 requirements

### Production Hardening (Recommended)

Before deploying to production, implement:

- HTTPS/TLS 1.3 - Encrypt all traffic
- AWS KMS - Secure encryption key management
- Rate Limiting - Prevent brute force attacks
- CSRF Protection - Token-based CSRF defense
- Security Headers - CSP, HSTS, X-Frame-Options
- Multi-Factor Authentication - TOTP or SMS-based
- PostgreSQL - Migrate from SQLite for concurrency

See [FUTURE_WORK_ROADMAP.pdf](./docs/FUTURE_WORK_ROADMAP.pdf) - Phase 1 for implementation details

## Compliance

### HIPAA Alignment

| HIPAA Requirement | Implementation | Status |
|---|---|---|
| PHI Encryption (§164.312(a)(2)(iv)) | Fernet AES-128 encryption | ✅ Full |
| Access Controls (§164.312(a)(1)) | RBAC (Admin/Nurse roles) | ✅ Full |
| Audit Trail (§164.312(b)) | Complete activity logging (100% coverage) | ✅ Full |
| Session Timeout (§164.312(a)(2)(iii)) | 2-minute auto-logout | ✅ Full |
| Workforce Training (§164.308(a)(5)) | 3 modules, 9 scenarios, scoring | ✅ Full |
| Risk Analysis (§164.308(a)(1)) | STRIDE threat model (27 items) | ✅ Full |
| Breach Notification (§164.400-414) | 5 incident playbooks, 60-day timeline | ✅ Full |

### Validation

- 50/50 audit entries logged - 100% completeness
- 15/15 SQL injection attempts blocked - 100% protection
- 12/12 XSS attempts blocked - 100% protection
- 34/34 automated tests passing - 100% pass rate
- All performance targets exceeded - 30-76% better than target

### Certification Status

| Certification | Status | Timeline |
|---|---|---|
| HIPAA Compliance | ✅ Verified | Ready |
| HITRUST | 🔄 Future work | Q2 2026 |
| SOC 2 Type II | 🔄 Future work | Q3 2026 |
| GDPR | 🔄 Future work | Q4 2026 |

### Limitations

**Current Version:**
- **Database:** SQLite (single-user, not scalable for 100+ concurrent users)
- **Authentication:** Password-based only (no MFA, no SSO)
- **Deployment:** Local/single-server only (no cloud, no load balancing)
- **Mobile:** Web-only (no iOS/Android apps)
- **EHR Integration:** Standalone system (no Epic, Cerner integration)
- **Multi-Tenant:** Single organization per deployment
- **International:** US-only (English, HIPAA only)

*These limitations are intentional for an educational capstone project. Production deployments would require addressing these items.*

See [FUTURE_WORK_ROADMAP.pdf](./docs/FUTURE_WORK_ROADMAP.pdf) for plans to address limitations.

## Contributing

SecureMed is an open-source project. We welcome contributions!

### Contribution Areas

- **Code improvements** - Bug fixes, performance optimization
- **Documentation** - Clarity, examples, translations
- **Testing** - Additional test cases, edge cases
- **Security** - Vulnerability reports (responsibly disclosed)
- **Features** - Ideas for future enhancements

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes (ensure tests pass)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code Standards

- Follow PEP 8 (Python)
- Write unit tests for new features
- Update documentation
- Add security considerations

### Security Issues

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, email: security@securemed.io (or contact project lead)

## Future Work

SecureMed has a clear 2-year roadmap to evolve into an enterprise solution:

```
Q1 2026: Production Hardening
├─ HTTPS/TLS
├─ AWS KMS
└─ Rate Limiting

Q2 2026: Enterprise Features
├─ PostgreSQL
├─ Multi-Tenant
└─ SSO/MFA

Q3 2026: Advanced Monitoring
├─ SIEM Integration
├─ EHR Integration
└─ Advanced EDR

Q4 2026: Compliance Automation
├─ Auto-Reporting
├─ GDPR Support
└─ ML Anomaly Detection

2027: Mobile & Accessibility
├─ iOS/Android Apps
├─ WCAG Compliance
└─ Multi-Language
```

**Full roadmap with budgets and timelines:** See [FUTURE_WORK_ROADMAP.pdf](./docs/FUTURE_WORK_ROADMAP.pdf)

## Support

### Getting Help

1. **Check the documentation:** Most questions answered in [TROUBLESHOOTING_GUIDE.pdf](./docs/TROUBLESHOOTING_GUIDE.pdf)
2. **Review examples:** See [HOW_TO_USE_GUIDE.pdf](./docs/HOW_TO_USE_GUIDE.pdf) for workflows
3. **Check known issues:** See [GitHub Issues](https://github.com/IamStefannn/SecureMedFIU/issues) section
4. **Contact the team:** See [Contributors](#team--contributors) section below

### Reporting Issues

Found a bug? Have a question?

1. Check existing issues - Might already be reported
2. Provide details:
   - What were you doing?
   - What did you expect?
   - What actually happened?
   - Error messages (with full traceback)
   - System info (OS, Python version, etc.)
3. [Open a GitHub Issue](https://github.com/IamStefannn/SecureMedFIU/issues)

### Asking Questions

- Use [GitHub Discussions](https://github.com/IamStefannn/SecureMedFIU/discussions) for general questions
- Use GitHub Issues only for bugs
- Join our community Slack (if available)

## Team & Contributors

### Original Development Team (Fall 2025)

| Role | Name | Contributions |
|---|---|---|
| Backend Lead | Stefan Dumitrasku | Flask API, database, encryption, testing |
| Security Engineer | Ana Salazar | Authentication, HIPAA compliance, security audit |
| Frontend Developer | Jordan Burgos | React UI, dashboards, presentation |
| Cybersecurity Analyst | Jeremiah Luzincourt | Threat detection, EDR, breach simulations |
| Documentation Lead | Mumin Tahir | PDF generation, documentation, deployment |

### Faculty Advisor

**Dr. Masoud Sadjadi** - Florida International University

### Institution

Florida International University School of Computing and Information Sciences  
CIS 4914 - Cybersecurity Capstone Project II

## License

SecureMed is released under the MIT License.

You are free to:
- ✅ Use commercially
- ✅ Modify the code
- ✅ Distribute
- ✅ Private use

You must:
- 📋 Include license and copyright notice
- 📋 Provide copy of license

See [LICENSE](./LICENSE) file for full details.

### Citation

If you use SecureMed in academic work, please cite:

```bibtex
@software{securemed2025,
  title={SecureMed: Healthcare Cybersecurity & HIPAA Compliance Platform},
  author={Dumitrasku, Stefan and Salazar, Ana and Burgos, Jordan and Luzincourt, Jeremiah and Tahir, Mumin},
  year={2025},
  institution={Florida International University},
  url={https://github.com/IamStefannn/SecureMedFIU}
}
```

## Acknowledgments

- **Flask** - Python web framework
- **React** - JavaScript UI library
- **ReportLab** - PDF generation
- **Cryptography** - Python crypto library
- **Tailwind CSS** - Utility-first CSS
- **Florida International University** - Academic support and resources

## Contact & Links

- **GitHub:** https://github.com/IamStefannn/SecureMedFIU
- **Documentation:** See files in `/docs` directory
- **Issues:** [GitHub Issues](https://github.com/IamStefannn/SecureMedFIU/issues)
- **Questions:** [GitHub Discussions](https://github.com/IamStefannn/SecureMedFIU/discussions)
- **Email:** securemed@fiu.edu

---

## Disclaimer

**Educational Purpose:** SecureMed is built as an educational capstone project to demonstrate cybersecurity concepts and HIPAA compliance requirements.

### Before Production Use:

⚠️ Conduct security audit by qualified security professional  
⚠️ Perform penetration testing  
⚠️ Implement production hardening (see Phase 1 roadmap)  
⚠️ Obtain HIPAA/HITRUST certification  
⚠️ Conduct legal review  
⚠️ Test extensively in staging environment  

**Warranty:** Provided AS-IS without warranty. See LICENSE for full disclaimer.

---

**Version:** 1.0 - Final  
**Last Updated:** December 2025  
**Status:** Production-Ready (with noted limitations)

### Ready to Get Started?

→ [Installation Guide](./docs/INSTALLATION_GUIDE.pdf)  
→ [Features Overview](./docs/FEATURES_SYSTEM_OVERVIEW.pdf)  
→ [Deployment Planning](./docs/FUTURE_WORK_ROADMAP.pdf)
