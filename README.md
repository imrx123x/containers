# 🚀 Flask Users App (Auth + Admin Panel + Audit Log)

A full-stack Flask application for user management with authentication, role-based access control, admin dashboard, and audit logging.

🔗 **Live Demo:** https://containers-am6s.onrender.com  
📘 **Swagger API Docs:** https://containers-am6s.onrender.com/apidocs/

---

## ✨ Features

### 🔐 Authentication & Authorization
- User registration & login
- Access token-based authentication
- Role-based access control (admin / user)
- Change password
- Edit own profile

### 👤 User Panel
- View profile
- Update name and email
- Change password

### 🛠 Admin Panel
- Create, update, delete users
- Search users
- Pagination
- Role visibility (admin/user)

### 📊 Dashboard
- Total users count
- Admin count
- Regular users count
- Latest registered user

### 🧾 Audit Log
- Tracks:
  - login
  - registration
  - profile updates
  - password changes
  - admin actions (create/update/delete user)
- Visible in admin panel

### 📘 API Documentation
- Swagger UI included (`/apidocs/`)
- Fully documented endpoints

### ⚙️ Infrastructure
- Docker support
- Render deployment ready
- Health checks (`/health`, `/health/db`)
- Logging with request ID
- Rate limiting (in-memory)

---

## 🧱 Tech Stack

- **Backend:** Flask
- **Database:** PostgreSQL
- **Auth:** Token-based (itsdangerous)
- **Frontend:** Jinja2 + CSS
- **Docs:** Flasgger (Swagger UI)
- **Deployment:** Render
- **Containerization:** Docker / Docker Compose

---

## 📸 Screens (what you get)

- Login & Register UI
- User profile with edit + password change
- Admin dashboard with stats
- User management panel
- Audit log panel

---

## 🧪 Running locally

### 1. Clone repo

```bash
git clone https://github.com/imrx123x/containers.git
cd containers