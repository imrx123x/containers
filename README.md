# 🚀 Flask Users App (Auth + Admin Panel + Audit Log)

A full-stack Flask application for user management with authentication, role-based access control, admin dashboard, and audit logging.

🔗 **Live Demo:** https://containers-am6s.onrender.com
📘 **Swagger API Docs:** https://containers-am6s.onrender.com/apidocs/

---

## ✨ Features

### 🔐 Authentication & Authorization

* User registration & login
* Access token-based authentication
* Role-based access control (admin / user)
* Change password
* Edit own profile

### 👤 User Panel

* View profile
* Update name and email
* Change password

### 🛠 Admin Panel

* Create, update, delete users
* Search users
* Pagination
* Role visibility (admin/user)

### 📊 Dashboard

* Total users count
* Admin count
* Regular users count
* Latest registered user

### 🧾 Audit Log

* Tracks:

  * login
  * registration
  * profile updates
  * password changes
  * admin actions (create/update/delete user)
* Visible in admin panel

### 📘 API Documentation

* Swagger UI included (`/apidocs/`)
* Fully documented endpoints

### ⚙️ Infrastructure

* Docker support
* Render deployment ready
* Health checks (`/health`, `/health/db`)
* Logging with request ID
* Rate limiting (in-memory)

---

## 🧱 Tech Stack

* **Backend:** Flask
* **Database:** PostgreSQL
* **Auth:** Token-based (itsdangerous)
* **Frontend:** Jinja2 + CSS
* **Docs:** Flasgger (Swagger UI)
* **Deployment:** Render
* **Containerization:** Docker / Docker Compose

---

## 📸 What you get

* Login & Register UI
* User profile with edit + password change
* Admin dashboard with stats
* User management panel
* Audit log panel

---

## 🧪 Running locally

### 1. Clone repo

```bash
git clone https://github.com/imrx123x/containers.git
cd containers
```

### 2. Run with Docker

```bash
docker-compose up --build
```

App will be available at:

```
http://localhost:5000
```

---

## ⚙️ Environment variables

Example:

```env
APP_ENV=development
SECRET_KEY=your-secret-key
DB_HOST=db
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
DB_PORT=5432
```

---

## 🔐 Authentication (IMPORTANT)

This app uses **Bearer tokens**.

### How to use token in API requests:

In Swagger or Postman, you must send header:

```
Authorization: Bearer <your_access_token>
```

⚠️ Important:

* You **must include the word `Bearer` before the token**
* Example:

```
Authorization: Bearer eyJhbGciOi...
```

---

## 📘 API Endpoints (summary)

### Auth

* `POST /api/auth/register`
* `POST /api/auth/login`
* `GET /api/auth/me`
* `PATCH /api/auth/me`
* `POST /api/auth/change-password`

### Users

* `GET /api/users`
* `GET /api/users/<id>`
* `POST /api/users` (admin)
* `PUT /api/users/<id>` (admin)
* `DELETE /api/users/<id>` (admin)

---

## 👨‍💻 How to create admin user

By default, users are created with role `user`.

To make admin:

```sql
UPDATE users
SET role = 'admin'
WHERE email = 'your@email.com';
```

---

## ❤️ Design decisions

* No paid migrations → DB is auto-created via `init_db()`
* Rate limiting implemented in-memory (simple but effective for demo)
* Audit log stored in DB for visibility
* Clean architecture:

  * routes
  * services
  * repository layer

---

## 📈 What this project demonstrates

* Full auth flow (register → login → profile)
* Role-based UI + backend security
* Admin dashboard with stats
* Production-ready patterns (logging, health checks)
* API documentation (Swagger)
* Audit logging system

---

## 🚀 Future improvements

* Password reset via token
* Soft delete users
* Redis-based rate limiting
* Email integration
* Better UI (React / SPA)

---

## 👤 Author

GitHub: https://github.com/imrx123x

---

## ⭐ If you like it

Give it a ⭐ on GitHub — it helps a lot!
