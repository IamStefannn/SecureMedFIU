# Testing Forgot Password Feature

## Step 1: Replace HTML File

**Replace your current file:**
templates/forgot_password.html

**With the new file:**
forgot_password_WORKING.html

## Step 2: Verify Route in webapp.py

Make sure this route exists in your webapp.py:

```python
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"].strip()
        dob = request.form["dob"].strip()
        ssn_last4 = request.form["ssn_last4"].strip()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND dob=? AND ssn_last4=?", 
                 (username, dob, ssn_last4))
        user = c.fetchone()
        conn.close()
        
        if user:
            session["reset_user"] = username
            return redirect(url_for("reset_password"))
        else:
            return render_template("forgot_password.html", error="Verification failed. Please check your information.")
    
    return render_template("forgot_password.html")
```

## Step 3: Test the Flow

### Test Case 1: Admin Account
1. Navigate to: http://127.0.0.1:5000/login
2. Click "Forgot Password?"
3. **You should see 3 fields:**
   - Username (text input)
   - Date of Birth (date picker)
   - Last 4 of SSN (text input with 4-digit limit)
4. Enter:
   - Username: `admin`
   - DOB: `1985-06-15`
   - SSN Last 4: `1234`
5. Click "Verify Identity"
6. Should redirect to reset password page

### Test Case 2: Nurse Account
1. Click "Forgot Password?" from login
2. Enter:
   - Username: `nurse`
   - DOB: `1990-03-22`
   - SSN Last 4: `5678`
3. Click "Verify Identity"
4. Should redirect to reset password page

### Test Case 3: Wrong Information
1. Click "Forgot Password?" from login
2. Enter:
   - Username: `admin`
   - DOB: `2000-01-01` (wrong)
   - SSN Last 4: `9999` (wrong)
3. Click "Verify Identity"
4. Should show error: "Verification failed. Please check your information."

## Step 4: Complete Password Reset

After successful verification:
1. Reset password page loads
2. Enter new password (min 8 characters)
3. Confirm password
4. Click "Reset Password"
5. See success message
6. Click "Go to Login"
7. Login with new password

## Expected Visual Appearance

The forgot password page should look like this:

┌─────────────────────────────────┐
│    🔐 Forgot Password           │
│                                 │
│  Verify your identity to        │
│  reset your password            │
│                                 │
│  ┌───────────────────────────┐ │
│  │ Security Verification     │ │
│  │ Required                  │ │
│  │ • Enter your username     │ │
│  │ • Provide date of birth   │ │
│  │ • Enter last 4 of SSN     │ │
│  └───────────────────────────┘ │
│                                 │
│  Username                       │
│  [________________]             │
│                                 │
│  Date of Birth                  │
│  [____/____/________]           │
│                                 │
│  Last 4 Digits of SSN          │
│  [____]                         │
│                                 │
│  [  Verify Identity  ]          │
│                                 │
│  ← Back to Login                │
└─────────────────────────────────┘

## Troubleshooting

### Issue: Still showing login form
**Solution:** 
1. Clear browser cache (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
2. Restart Flask server
3. Verify correct template file is in templates/ folder

### Issue: Fields not appearing
**Solution:**
1. Check browser console for JavaScript errors
2. View page source to ensure HTML is correct
3. Make sure you replaced the right file

### Issue: "Template not found" error
**Solution:**
1. Verify file is named exactly: `forgot_password.html`
2. Verify file is in `templates/` folder
3. Check Flask is looking in correct directory

### Issue: Verification always fails
**Solution:**
1. Check database has dob and ssn_last4 columns
2. Run: `python setup_database.py` to recreate with new columns
3. Verify users have security data populated

## Database Schema Check

Run this in terminal to verify database:

```bash
sqlite3 securemed.db "PRAGMA table_info(users);"
```

Expected output should include:
...
4|dob|TEXT|0||0
5|ssn_last4|TEXT|0||0

If missing, recreate database:
rm securemed.db
python setup_database.py

---

**After following these steps, forgot password should work perfectly!** ✅
