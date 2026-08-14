# Dynamic QR AI Platform 🤖🔐

> **An AI-powered dynamic QR infrastructure platform that lets users create, manage, monitor, and secure QR codes with real-time URL risk analysis.**

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)](https://react.dev/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)](https://www.sqlite.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT-black)](https://jwt.io/)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange)]()

---

## 🚀 Overview

Dynamic QR AI is a full-stack QR infrastructure platform designed around one core idea:

> **A QR code should remain useful and controllable even after it has been printed or distributed.**

Instead of encoding a destination directly into a QR code, the platform creates a **dynamic QR link** that redirects through the backend.

This allows the destination URL to be changed later without replacing the physical QR code.

The platform also introduces an **AI security layer** that analyzes URLs and assigns a risk score before they are used by the QR infrastructure.

---

## 🎯 Problem

Traditional QR codes are often static.

Once a QR code is printed:

* The destination cannot easily be changed
* There is limited control over the destination
* Scan activity is difficult to monitor
* Malicious or suspicious URLs can potentially be distributed through QR codes

Dynamic QR AI addresses these limitations through:

**Dynamic redirection + authentication + analytics + AI-powered URL security.**

---

## ✨ Current Features

### 🔗 Dynamic QR Generation

Create a QR code that points to a controlled backend URL rather than directly to the final destination.

```text
QR Code
   ↓
/q/{qr_id}
   ↓
Current destination URL
```

The destination can be updated without generating a new QR code.

---

### 🔄 Dynamic URL Updates

The destination associated with a QR code can be changed through the backend API.

Example:

```text
Old:
https://example.com/page1

        ↓ update

New:
https://example.com/page2
```

The physical QR code remains unchanged.

---

### 📊 Scan Analytics

Each QR scan is tracked by the backend.

Current analytics include:

* QR ID
* Destination URL
* Scan count
* Active/inactive state

---

### 🔐 JWT Authentication

The platform includes:

* User registration
* User login
* Password hashing
* JWT authentication
* Protected QR management endpoints

Authenticated users can manage their QR infrastructure through protected APIs.

---

### 🤖 AI URL Security Engine

A separate AI Engine microservice analyzes URLs before QR creation.

The current engine evaluates indicators such as:

* HTTPS usage
* Suspicious keywords
* Domain characteristics
* URL patterns

It produces:

```text
Risk Score
Security Status
Detection Reasons
```

Example:

```json
{
  "domain": "free-bank-login-gift",
  "risk_score": 105,
  "status": "DANGEROUS 🔴",
  "reasons": [
    "No HTTPS detected",
    "Suspicious keyword login",
    "Suspicious keyword password",
    "Suspicious keyword bank",
    "Suspicious keyword free",
    "Suspicious keyword gift"
  ]
}
```

---

## 🏗️ Architecture

The project is organized as a multi-service application:

```text
                         ┌─────────────────────┐
                         │      React UI       │
                         │   localhost:5173    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   FastAPI Backend   │
                         │   localhost:8000    │
                         └───────┬───────┬─────┘
                                 │       │
                       ┌─────────┘       └──────────┐
                       ▼                            ▼
              ┌────────────────┐          ┌─────────────────┐
              │ SQLite + ORM   │          │   AI Engine     │
              │   SQLAlchemy   │          │ localhost:9000  │
              └────────────────┘          └─────────────────┘
```

### Services

| Service   | Technology          |   Port | Purpose                            |
| --------- | ------------------- | -----: | ---------------------------------- |
| Frontend  | React + Vite        | `5173` | User interface                     |
| Backend   | FastAPI             | `8000` | API, QR management, authentication |
| AI Engine | FastAPI + Python    | `9000` | URL security analysis              |
| Database  | SQLite + SQLAlchemy |      — | Users and QR data                  |

---

## 🛠️ Tech Stack

### Frontend

* React
* Vite
* JavaScript
* Axios
* React Router
* Lucide React
* Tailwind CSS

### Backend

* Python
* FastAPI
* Uvicorn
* SQLAlchemy
* SQLite
* Pydantic
* JWT
* Passlib
* bcrypt
* QRCode
* Pillow
* Requests

### AI Engine

* Python
* FastAPI
* Scikit-learn
* tldextract
* Requests
* python-dotenv

---

## 📁 Project Structure

```text
DynamicQR-AI/
│
├── ai-engine/
│   ├── main.py
│   └── requirements.txt
│
├── backend/
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── qr_codes.db
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── package-lock.json
└── requirements.txt
```

---

## 🔌 Backend API

### Authentication

```text
POST /register
POST /login
```

### QR Management

```text
POST /create-qr
GET  /q/{qr_id}
PUT  /update-qr/{qr_id}
GET  /details/{qr_id}
```

### AI Engine

```text
GET  /
POST /scan
```

---

## 🧪 Example Workflow

### 1. Register

```text
POST /register
```

### 2. Login

```text
POST /login
```

Receive a JWT access token.

### 3. Authorize

Use the JWT token to access protected endpoints.

### 4. Create QR

```text
POST /create-qr
```

Example destination:

```text
https://github.com/prashantVerse12
```

### 5. AI Analysis

The URL is sent to the AI Engine for security analysis.

### 6. QR Creation

If the URL passes the configured security checks, the backend generates a dynamic QR.

### 7. Scan

```text
/q/{qr_id}
```

The backend:

1. Finds the QR
2. Checks whether it is active
3. Increments the scan counter
4. Redirects the user to the current destination

### 8. Update

The destination can later be changed while keeping the same QR code.

---

## 🔐 Security Model

The current platform uses multiple security layers:

```text
User
 │
 ▼
JWT Authentication
 │
 ▼
Protected API
 │
 ▼
AI URL Analysis
 │
 ├── SAFE 🟢
 ├── SUSPICIOUS 🟡
 └── DANGEROUS 🔴
 │
 ▼
Dynamic QR Infrastructure
```

This architecture is designed to separate:

* Identity and access control
* QR infrastructure
* URL security analysis

---

## 📈 Current Development Status

### Completed

* [x] Project architecture
* [x] FastAPI backend
* [x] React/Vite frontend foundation
* [x] SQLite database
* [x] SQLAlchemy models
* [x] Dynamic QR generation
* [x] Dynamic QR redirection
* [x] QR destination updates
* [x] Scan counting
* [x] QR image serving
* [x] User registration
* [x] Password hashing
* [x] JWT login
* [x] Protected API endpoints
* [x] AI Engine microservice
* [x] URL risk scoring
* [x] Suspicious URL detection
* [x] AI security response integration

### In Progress

* [ ] Production-ready React SaaS dashboard
* [ ] Login/Register UI
* [ ] QR management dashboard
* [ ] AI security visualization
* [ ] Advanced analytics
* [ ] Production deployment
* [ ] Improved ML-based URL classification

---

## 🧠 Engineering Approach

Development follows an iterative engineering workflow:

```text
Understand
    ↓
Implement
    ↓
Test
    ↓
Document
    ↓
Commit
    ↓
Continue
```

Each feature is tested before moving to the next development phase.

---

## 🔮 Future Roadmap

### Phase 9 — SaaS Dashboard

* Modern React dashboard
* QR management interface
* AI security cards
* Risk visualization
* Analytics dashboard

### Phase 10 — Advanced Security Intelligence

* Better URL feature extraction
* ML classification
* Domain reputation signals
* More sophisticated phishing detection
* Explainable risk scoring

### Phase 11 — Production Infrastructure

* PostgreSQL
* Environment-based secrets
* Docker
* Cloud deployment
* HTTPS
* Production authentication
* Monitoring and logging

---

## 💡 Why This Project?

Dynamic QR AI combines several real-world engineering concepts in one system:

**Full-Stack Development**

React + FastAPI

**Backend Engineering**

REST APIs + database + authentication

**Cybersecurity**

JWT + URL threat detection + phishing indicators

**AI/ML**

Risk scoring and URL classification

**Microservices**

Independent AI security service

This makes the project a practical demonstration of building and integrating multiple production-oriented software components.

---

## 👨‍💻 Author

**Prashant Kumar**

B.Tech — Computer Science & Engineering
Cyber Security

GitHub: [@prashantVerse12](https://github.com/prashantVerse12)

---

## ⭐ Project Status

**Active Development 🚧**

The core dynamic QR infrastructure, authentication system, database layer, and AI URL security engine are implemented. The project is currently being evolved into a complete AI-powered SaaS dashboard.
