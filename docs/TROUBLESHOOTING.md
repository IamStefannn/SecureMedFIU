# SecureMed - Troubleshooting Guide

## Common Issues and Solutions

---

## Issue 1: "ModuleNotFoundError: No module named 'flask'"

### Symptoms
```
Traceback (most recent call last):
  File "/path/to/webapp.py", line 1, in <module>
    from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
ModuleNotFoundError: No module named 'flask'
```

### Root Cause
Flask and other required dependencies are not installed in your Python environment.

### Solution

**Option 1: Use Virtual Environment (Recommended)**
```bash
# Navigate to project directory
cd /Users/stefandumitrasku/Downloads/Cap_Finaldev

# Activate the virtual environment
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the application
python webapp.py
```

**Option 2: Install System-Wide**
```bash
# Install dependencies globally
pip3 install -r requirements.txt

# Run with python3
python3 webapp.py
```

**Option 3: Create New Virtual Environment**
```bash
# Create new virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python webapp.py
```

### How to Verify Fix
After running the commands, you should see:
```
🚀 SecureMed running on http://127.0.0.1:5000/login
   [Credentials hidden for security]
   Check CREDENTIALS.txt for login info
 * Serving Flask app 'webapp'
 * Debug mode: on
```

---

## Issue 2: "jinja2.exceptions.TemplateNotFound: login.html"

### Symptoms
```
jinja2.exceptions.TemplateNotFound: login.html

Traceback (most recent call last)
File "/Users/stefandumitrasku/Downloads/Project_dev1/webapp.py", line 255, in login_page
```

### Root Cause
One or more of the following:
1. Flask app is running from the wrong directory
2. Multiple Flask instances are running from different directories
3. Templates folder is not in the same directory as webapp.py

### Solution

**Step 1: Kill All Running Flask Processes**
```bash
# Find Flask processes
ps aux | grep webapp.py

# Kill all Flask processes
pkill -9 -f "webapp.py"

# OR kill specific process by PID
kill -9 <PID>

# Verify they're stopped
ps aux | grep webapp.py
```

**Step 2: Verify You're in the Correct Directory**
```bash
# Check current directory
pwd

# Should show something like:
# /Users/stefandumitrasku/Downloads/Cap_Finaldev

# List contents to verify
ls -la

# You should see:
# - webapp.py
# - templates/ directory
# - requirements.txt
```

**Step 3: Verify Templates Exist**
```bash
# Check templates directory
ls -la templates/

# Should show login.html and other templates
```

**Step 4: Start Flask from Correct Directory**
```bash
# Make sure you're in the project root
cd /Users/stefandumitrasku/Downloads/Cap_Finaldev

# Use virtual environment
source venv/bin/activate

# Start the app
python webapp.py
```

### How to Verify Fix
The error traceback should now show the CORRECT path:
```
File "/Users/stefandumitrasku/Downloads/Cap_Finaldev/webapp.py", line 255
```

NOT:
```
File "/Users/stefandumitrasku/Downloads/Project_dev1/webapp.py", line 255
```

---

## Issue 3: Port Already in Use

### Symptoms
```
OSError: [Errno 48] Address already in use
```

### Root Cause
Another Flask instance or application is using port 5000.

### Solution

**Option 1: Kill Process Using Port 5000**
```bash
# Find process on port 5000
lsof -ti:5000

# Kill the process
kill -9 $(lsof -ti:5000)

# Verify port is free
lsof -ti:5000
# (should return nothing)
```

**Option 2: Use Different Port**
Edit `webapp.py` to use a different port:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed from 5000 to 5001
```

---

## Issue 4: Database Locked Error

### Symptoms
```
sqlite3.OperationalError: database is locked
```

### Root Cause
Multiple processes trying to access the database simultaneously.

### Solution
```bash
# Kill all Flask processes
pkill -9 -f "webapp.py"

# Wait a moment
sleep 2

# Restart the app
source venv/bin/activate
python webapp.py
```

---

## Issue 5: Session Timeout (Auto Logout)

### Symptoms
Automatically logged out after 2 minutes of inactivity.

### Root Cause
Security feature - sessions expire after 2 minutes by default.

### Solution
This is by design for security. When you see the warning:
```
⚠️ Your session will expire in 30 seconds due to inactivity
```

Click **"Stay Logged In"** to refresh the session.

To disable (not recommended for production):
Edit `webapp.py` around line 8:
```python
app.permanent_session_lifetime = timedelta(minutes=30)  # Increase from 2 to 30
```

---

## Issue 6: Cannot Find CREDENTIALS.txt

### Symptoms
Cannot find login credentials file.

### Solution
The credentials are hardcoded in the database. Default credentials:

**Admin Account:**
- Username: `admin`
- Password: `Admin123!`

**Team Member Accounts:**
- Username: `stefan` / Password: `Stefan123!`
- Username: `ana` / Password: `Ana123!`
- Username: `jordan` / Password: `Jordan123!`
- Username: `jeremiah` / Password: `Jeremiah123!`
- Username: `mumin` / Password: `Mumin123!`

Pattern: `[Name]123!`

---

## Issue 7: Virtual Environment Not Activating

### Symptoms
```bash
source venv/bin/activate
# Nothing happens or command not found
```

### Solution

**On macOS/Linux:**
```bash
source venv/bin/activate

# Your prompt should change to show (venv)
# Example: (venv) user@computer:~/project$
```

**On Windows:**
```bash
venv\Scripts\activate
```

**If venv doesn't exist:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Issue 8: "python: command not found"

### Symptoms
```bash
python webapp.py
# zsh: command not found: python
```

### Root Cause
Python 3 is installed as `python3` not `python` on macOS.

### Solution
Use `python3` instead:
```bash
python3 webapp.py
```

OR activate virtual environment first:
```bash
source venv/bin/activate
python webapp.py  # Works inside venv
```

---

## Issue 9: Permission Denied Errors

### Symptoms
```
PermissionError: [Errno 13] Permission denied: 'securemed.db'
```

### Solution
```bash
# Fix file permissions
chmod 644 securemed.db

# If still failing, check directory permissions
chmod 755 .
```

---

## Issue 10: Browser Shows "Cannot Connect"

### Symptoms
Browser shows "This site can't be reached" at http://127.0.0.1:5000

### Solution

**Step 1: Verify Flask is Running**
```bash
# Check if process is running
ps aux | grep webapp.py

# Check if port is open
lsof -ti:5000
```

**Step 2: Check Flask Output**
Look for this message:
```
* Running on http://127.0.0.1:5000
```

**Step 3: Try Alternative URLs**
- http://localhost:5000
- http://127.0.0.1:5000/login
- http://0.0.0.0:5000

**Step 4: Check Firewall**
Ensure your firewall isn't blocking port 5000.

---

## General Troubleshooting Checklist

When something goes wrong, try these steps in order:

1. **Kill All Flask Processes**
   ```bash
   pkill -9 -f "webapp.py"
   ```

2. **Verify You're in Correct Directory**
   ```bash
   pwd
   ls -la templates/
   ```

3. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

4. **Verify Dependencies Installed**
   ```bash
   pip list | grep -i flask
   ```

5. **Restart the Application**
   ```bash
   python webapp.py
   ```

6. **Check for Errors in Terminal**
   Look for error messages in the Flask output

7. **Clear Browser Cache**
   Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

---

## Quick Reference: Starting the App

### Every Time You Start the App:

```bash
# 1. Navigate to project
cd /Users/stefandumitrasku/Downloads/Cap_Finaldev

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start Flask
python webapp.py

# 4. Open browser
# Go to: http://127.0.0.1:5000/login
```

### Stopping the App:

```bash
# In the terminal where Flask is running:
Press Ctrl+C

# OR from another terminal:
pkill -f "webapp.py"
```

---

## Getting Help

If you encounter an error not listed here:

1. **Read the full error message** - The last line usually tells you what's wrong
2. **Check the traceback** - Shows which file and line number caused the issue
3. **Verify file paths** - Make sure you're in the right directory
4. **Check Flask output** - Look for warnings or errors in the terminal
5. **Try Full Reset** - Kill all processes and start fresh

---

## Common Error Messages Explained

| Error | Meaning | Solution |
|-------|---------|----------|
| `ModuleNotFoundError` | Python package not installed | Install with pip |
| `TemplateNotFound` | Wrong directory or missing file | Check pwd and ls |
| `Address already in use` | Port 5000 is occupied | Kill the process |
| `Permission denied` | File permissions issue | Use chmod |
| `database is locked` | Multiple processes accessing DB | Kill all Flask instances |
| `command not found: python` | Use python3 instead | Run `python3` |

---

*Last Updated: November 2024*
*For SecureMed Capstone Project*
