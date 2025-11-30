# 🚀 Quick Installation Guide

Welcome! Follow these simple steps to get your application up and running.

---

## 💻 Windows Users (VS Code)

### Step 1: Open Your Terminal
Press `` Ctrl+` `` or go to **View → Terminal** in VS Code

### Step 2: Navigate to Your Project
```bash
cd path\to\Cap_Finaldev
```
> 💡 **Tip:** Replace `path\to\` with your actual folder location

### Step 3: Create a Virtual Environment
```bash
python -m venv venv
```
> ⏱️ This takes about 10-30 seconds

### Step 4: Activate the Virtual Environment
```bash
venv\Scripts\activate
```

> ⚠️ **Got an error?** Run this command first, then try again:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Step 5: Install Required Packages
```bash
pip install -r requirements.txt
```
> ⏱️ This may take 1-2 minutes

### Step 6: Launch the Application
```bash
python webapp.py
```
> ✅ You should see output indicating Flask is running

### Step 7: Open in Your Browser
Click this link or paste it in your browser: **http://127.0.0.1:5000/login**

---

## 🍎 macOS / Linux Users

### Step 1: Open Terminal & Navigate
```bash
cd /path/to/Cap_Finaldev
```
> 💡 **Tip:** You can drag the folder into Terminal to auto-fill the path

### Step 2: Create a Virtual Environment
```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment
```bash
source venv/bin/activate
```
> ✅ Your prompt should now show `(venv)` at the beginning

### Step 4: Install Required Packages
```bash
pip install -r requirements.txt
```

### Step 5: Launch the Application
```bash
python webapp.py
```

### Step 6: Open in Your Browser
Click this link or paste it in your browser: **http://127.0.0.1:5000/login**

---

## 🔐 Default Login Credentials

Use these to log in for the first time:

| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `Admin123!`|

---

## 🛑 Stopping the Application

When you're done, press **`Ctrl+C`** in the terminal where Flask is running.

To deactivate the virtual environment:
```bash
deactivate
```

---

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
1. Make sure you see `(venv)` in your terminal prompt
2. If not, activate the virtual environment again (Step 4)
3. Run `pip install -r requirements.txt` again

---

### Problem: "Address already in use"

This means port 5000 is already being used.

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID  /F
```
> Replace `<PID>` with the number from the first command

**macOS/Linux:**
```bash
lsof -ti:5000 | xargs kill -9
```

---

### Problem: "Can't find templates" or 404 errors

**Solution:**
- Make sure you're running `python webapp.py` from inside the `Cap_Finaldev` folder
- Verify the `templates/` folder exists in the same directory as `webapp.py`

---

## 🎯 First Time Setup

After logging in successfully:

1. Click the **"⚡ Quick Setup"** button in the dashboard
2. This automatically creates:
   - ✅ 5 sample patients with realistic data
   - ✅ Task assignments for testing
   - ✅ Sample security vulnerabilities
   - ✅ Compliance violations for demonstration

> 💡 **Note:** This is optional but recommended for exploring all features!

---

## 📚 Need More Help?

- **Detailed User Guide:** [docs/HOW_TO_USE.md](docs/HOW_TO_USE.md)
- **Full Documentation:** [README.md](README.md)
- **Having issues?** Check the Troubleshooting section above

---