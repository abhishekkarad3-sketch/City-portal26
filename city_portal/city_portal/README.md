# 🏙️ City Portal — Smart City Services Web Application

A full-stack web application built with **Flask** (backend) and **HTML/CSS/JS** (frontend).

---

## ✨ Features

- 🌙 **Dark / Light Mode** toggle (persists across sessions)
- 🌐 **3 Languages**: English, हिंदी (Hindi), मराठी (Marathi) — full UI translation
- 🔐 Login & Sign Up
- 📊 User Dashboard with booking stats
- 🔧 Services: Electrician, Plumber, Internet, Computer Repair, CCTV
- 📅 Appointment Booking with date/time selection
- 💬 Booking Messages & Status Notifications
- ⭐ 1–5 Star Rating System
- 📝 Written Feedback
- 👤 Profile Page with Service History
- 🛠️ Admin Panel: add technicians, update booking statuses, view ratings
- 🔍 Search & filter technicians
- 📱 Fully Responsive (mobile-friendly)

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install flask
```

### 2. Run the app
```bash
cd city_portal
python app.py
```

### 3. Open browser
```
http://localhost:5000
```

---

## 🔑 Demo Credentials

| Role  | Email                     | Password  |
|-------|---------------------------|-----------|
| User  | demo@city.com             | demo123   |
| Admin | admin@cityportal.com      | admin123  |

---

## 🌐 Language Switching

Click the **EN / हि / म** buttons in the top navigation bar.
All text on every page will instantly switch to the selected language.

## 🎨 Theme Toggle

Click the **☀️ / 🌙** button to toggle between **Dark** and **Light** mode.
Your preference is saved automatically.

---

## 📁 Project Structure

```
city_portal/
├── app.py                    # Flask backend
├── city_portal.db            # SQLite database (auto-created)
├── requirements.txt
├── static/
│   ├── css/style.css         # All styles + dark/light themes
│   └── js/
│       ├── translations.js   # English, Hindi, Marathi translations
│       └── main.js           # Theme toggle, language switcher, animations
└── templates/
    ├── base.html             # Shared layout (navbar, footer)
    ├── login.html
    ├── signup.html
    ├── dashboard.html
    ├── services.html
    ├── book.html
    ├── bookings.html
    ├── messages.html
    ├── rate.html
    ├── profile.html
    └── admin.html
```

---

## 🛠️ Tech Stack

- **Backend**: Python Flask, SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Fonts**: Syne (headings) + DM Sans (body)
- **Design**: CSS Variables for theming, responsive grid layout
