# VoteSecure — Online Voting System

A secure, accessible, full-featured online voting system built with Django 4.x, MySQL, and vanilla JavaScript.

This is the **complete, updated build** including all bug fixes and new features:
- ✅ Session timeout fixed (5 minutes, no false-positive logout)
- ✅ Election auto-close when end time passes
- ✅ Admin/Voter login role toggle
- ✅ Voter self-registration
- ✅ Profile page with voting history + password change
- ✅ Dark mode toggle
- ✅ Animated results page with winner reveal + live prediction
- ✅ Export results to Excel & PDF
- ✅ Email notifications to voters
- ✅ Mobile responsive improvements
- ✅ Clean logout button styling

---

## 🗂️ Project Structure

```
voting_system/
├── voting_system/          # Django project config (settings, urls, wsgi)
├── accounts/                # Auth, MFA/OTP, voter registration, profile, audit logs
├── elections/                # Election model (auto-close fix included)
├── candidates/               # Candidate profiles (photo, party symbol)
├── votes/                     # Voting logic, transaction hash receipts
├── dashboard/                 # Admin/voter dashboards, results, export, email, REST API
├── templates/                 # All HTML templates
├── static/
│   ├── css/main.css           # Complete CSS (dark mode, WCAG 2.1 AA)
│   └── js/                    # main.js, session-timer.js, i18n.js, darkmode.js, sw.js
├── requirements.txt
└── manage.py
```

---

## 🚀 Setup Instructions (Fresh Install)

### 1. Prerequisites
- Python 3.10+
- MySQL 8.0+ (make sure `mysql` command is in your system PATH)
- pip

### 2. Extract the ZIP
Unzip this file to your desired location, e.g.:
```
C:\Users\YourName\OneDrive\Desktop\VoteSecure\
```

### 3. Create Virtual Environment
```bash
cd voting_system
python -m venv .env
source .env/Scripts/activate      # Windows Git Bash
# OR
.env\Scripts\activate.bat         # Windows CMD
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Create MySQL Database
Open MySQL command line:
```bash
mysql -u root -p
```
Then run:
```sql
CREATE DATABASE voting_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

### 6. Configure Database Connection
Open `voting_system/settings.py` and update the `DATABASES` section with your MySQL password:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'voting_db',
        'USER': 'root',
        'PASSWORD': 'YOUR_MYSQL_PASSWORD',   # ← update this
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 7. Run Migrations
```bash
python manage.py makemigrations accounts elections candidates votes
python manage.py migrate
```

### 8. Create Admin User
```bash
python manage.py createsuperuser
```
Enter email, first name, last name, password.

Then set the role to admin:
```bash
python manage.py shell
```
```python
from accounts.models import User
u = User.objects.get(email='your@email.com')
u.role = 'admin'
u.save()
exit()
```

### 9. Run the Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 📧 Email / OTP Setup

By default, if SMTP isn't configured, OTP codes print directly to your terminal:
```
[DEV] OTP for user@email.com: 123456
```

To enable real email (Gmail example):
1. Enable 2-Step Verification on your Google Account
2. Generate an **App Password** (Google Account → Security → App Passwords)
3. Update `settings.py`:
```python
EMAIL_HOST_USER = 'your@gmail.com'
EMAIL_HOST_PASSWORD = 'your-16-char-app-password'
```

---

## 🔐 Security Features

| Feature | Implementation |
|---------|-----------------|
| MFA/OTP | 6-digit OTP via email, 10-min expiry |
| Password Hashing | Django's PBKDF2 |
| CSRF Protection | Django middleware |
| Session Timeout | 5-minute inactivity, resets on activity |
| Role-Based Access | Admin/Voter login toggle + permission checks |
| One Vote Per User | DB-level `unique_together` constraint |
| Audit Logging | Logins, votes, IPs — ballot choice NOT logged |
| Auto-Close Elections | Status auto-updates to "closed" after end time |
| DevTools Disable | Right-click/F12 blocked on ballot page |

---

## 🎨 New Features Guide

### Admin/Voter Login Toggle
On the login page, switch between "Voter Login" and "Admin Login" tabs.

### Voter Self-Registration
Click "Register as New Voter" on the login page to create a new voter account without admin intervention.

### Dark Mode
Click the 🌙/☀️ icon in the navbar. Preference is saved in browser localStorage.

### Profile Page
Click your name in the navbar to view personal info, voter details, voting history, and change password.

### Results Page with Winner Reveal
From Admin Dashboard → Elections table → click "📊 Results" for any election. Shows animated winner card and live leader prediction for active elections.

### Export Results
From the Elections table, click "📥 Excel" or "📄 PDF" to download results.

### Send Email Notifications
Admin Dashboard → Quick Actions → "📧 Send Email" to message all voters or only those who haven't voted.

---

## 📊 Database Schema

```
users            — Custom user model (email, role, hashed password)
voter_profiles   — Voter info (voter_id, has_voted, constituency)
otp_records      — MFA OTP codes (single-use, expiring)
elections        — Election config (auto-closes when end_datetime passes)
candidates       — Candidate profiles (photo, party_symbol, bio)
votes            — Cast votes (transaction_hash, unique per voter/election)
audit_logs       — Activity log (no ballot choices stored)
```

---

## 🗳️ Voter Flow

1. Login → choose "Voter Login" tab → enter email + password
2. OTP → 6-digit code (check terminal if email not configured)
3. Dashboard → see active elections
4. Ballot → select candidate → confirm in modal
5. Receipt → transaction hash + downloadable PDF
6. Profile → view voting history anytime

## 📈 Admin Flow

1. Login → choose "Admin Login" tab
2. Create elections, add candidates with photos
3. Upload voter CSV or let voters self-register
4. Monitor live turnout charts (auto-refresh every 5s)
5. View results with winner announcement after election closes
6. Export results to Excel/PDF, send email notifications

---

## 🔧 Common Issues & Fixes

**"mysql: command not found"**
→ Add MySQL's `bin` folder to your system PATH (e.g. `C:\Program Files\MySQL\MySQL Server 8.4\bin`)

**"Access denied for user 'root'@'localhost'"**
→ Check your password in `settings.py` matches what you set in MySQL

**Election form keeps redirecting after a few seconds**
→ This was a session timeout bug — already fixed (now 5 minutes, and the AJAX check no longer false-triggers)

**Election shows "Active" after end time has passed**
→ Already fixed — dashboard auto-closes expired elections on every page load

---

## 📦 Updating Your GitHub Repository

If you already have a GitHub repo set up:
```bash
cd voting_system
git add .
git commit -m "Add new features: dark mode, profile page, results, export, email notifications"
git push origin main
```

If this is a fresh repo:
```bash
cd voting_system
git init
git add .
git commit -m "Initial commit - VoteSecure Online Voting System"
git remote add origin https://github.com/YOUR_USERNAME/VoteSecure-Online-Voting-System.git
git branch -M main
git push -u origin main
```

When prompted for credentials, use your GitHub username and a **Personal Access Token** (not your account password) — generate one at:
GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic) → check "repo" scope.

---

## 🏭 Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Generate new `SECRET_KEY`
- [ ] Enable HTTPS (`SECURE_SSL_REDIRECT = True`)
- [ ] Configure real SMTP server
- [ ] Run `python manage.py collectstatic`
- [ ] Use gunicorn + nginx
- [ ] Set up database backups
