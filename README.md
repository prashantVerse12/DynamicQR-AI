# DynamicQR-AI

### One QR. Change the content anytime. No reprinting.

DynamicQR-AI is a full-stack dynamic QR platform that separates the **printed QR code** from the **content it serves**.

Instead of encoding a final destination directly into a QR code, each QR points to a stable backend route. The content behind that route can then be changed, versioned, and managed without generating a new QR.

**Create once → Print once → Change later.**

🌐 **Live Demo:** https://dynamicqr-frontend.onrender.com

---

## Why Dynamic QR?

A normal QR code is effectively static.

If a restaurant changes its menu, an event changes its registration page, or a campaign changes its landing page, the printed QR may need to be replaced.

DynamicQR-AI introduces a layer between the QR and its destination:

```text
Printed QR
    │
    ▼
Stable DynamicQR URL
    │
    ▼
Current Published Content
    │
    ├── URL
    ├── TEXT
    └── FORM
```

The QR image stays the same while the published content can change.

This makes the same QR useful for:

- Menus
- Events
- Campaigns
- Announcements
- Landing pages
- Information boards
- Simple forms
- Frequently changing content

---

## Current Status

**Early MVP — deployed for real-user testing.**

The core dynamic QR workflow is live and the project is being developed with real user feedback in mind.

### Working today

- Dynamic QR generation
- Stable QR IDs
- URL, TEXT, and FORM content
- Content updates without changing the QR
- Content versioning
- Public QR resolution
- Scan counting
- User registration and login
- JWT-based authentication
- QR ownership and management
- React dashboard
- QR image generation
- PostgreSQL deployment
- Separate URL security analysis service

The project is intentionally still an MVP. The current focus is validating the core product before expanding into a larger SaaS platform.

---

## Product

### 1. Create

Create a QR code and choose what it should serve:

```text
URL
TEXT
FORM
```

### 2. Print

The generated QR can be printed or distributed.

### 3. Change

Update the content later without generating another QR.

### 4. Resolve

Anyone scanning the QR reaches the latest published version.

### 5. Track

The platform records scan counts and exposes QR information through the dashboard.

---

## Core Features

### Dynamic QR Resolution

Each QR uses a stable identifier:

```text
/q/{qr_id}
```

The backend resolves the currently published content instead of storing the final destination directly inside the QR image.

### Multi-Content Support

| Type | Behavior |
|---|---|
| `URL` | Redirects to the destination |
| `TEXT` | Returns plain text |
| `FORM` | Displays a safe, display-only form |

### Content Versioning

Each QR can have multiple content versions.

Only one version is published at a time.

```text
QR
 │
 ├── Version 1
 ├── Version 2
 ├── Version 3  ← Published
 └── Version 4
```

This allows the QR to remain stable while its content evolves.

### Authentication

The dashboard supports:

- Registration
- Login
- JWT authentication
- Protected QR management
- Ownership checks

### Scan Analytics

Each public QR resolution increments its scan counter.

The dashboard exposes the current scan count for managed QR codes.

### URL Security Analysis

URL content is sent to a separate FastAPI security engine during creation and updates.

The current scanner provides heuristic risk analysis using signals such as:

- HTTPS usage
- Suspicious keywords
- URL length

The result includes:

```text
Domain
Risk score
Status
Reasons
```

The scanner is a security signal, **not a guarantee that a destination is safe**.

---

## How It Works

```text
                    ┌──────────────────────┐
                    │   React Dashboard    │
                    │  Create / Update QR  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │                      │
                    │ Authentication       │
                    │ QR lifecycle         │
                    │ Content validation   │
                    │ Versioning           │
                    │ Resolution            │
                    └───────┬───────┬──────┘
                            │       │
                ┌───────────┘       └──────────────┐
                ▼                                  ▼
       ┌─────────────────┐                ┌─────────────────┐
       │ PostgreSQL      │                │  AI Security    │
       │ / SQLite        │                │     Engine      │
       │                 │                │                 │
       │ Users           │                │ URL analysis    │
       │ QR codes        │                │ Risk scoring    │
       │ Versions        │                │                 │
       └─────────────────┘                └─────────────────┘


                         PUBLIC SCAN

                        Printed QR
                            │
                            ▼
                      /q/{qr_id}
                            │
                            ▼
                  Published ContentVersion
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
            URL            TEXT           FORM
             │              │              │
             ▼              ▼              ▼
          302 Redirect   text/plain    Safe HTML
```

---

## Architecture

| Component | Technology | Responsibility |
|---|---|---|
| Frontend | React, Vite, Axios | Dashboard and QR management |
| Backend | Python, FastAPI, SQLAlchemy | API, authentication, QR lifecycle, content resolution |
| AI Engine | Python, FastAPI | URL risk analysis |
| Database | SQLite / PostgreSQL | Users, QR codes, content versions |
| Migrations | Alembic | Database schema migrations |

### Local Ports

| Service | Port |
|---|---:|
| Frontend | `5173` |
| Backend | `8000` |
| AI Engine | `9000` |

---

## Repository Structure

```text
DynamicQR-AI/
│
├── ai-engine/
│   ├── main.py
│   └── scanner.py
│
├── backend/
│   ├── auth.py
│   ├── config.py
│   ├── content.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── requirements.txt
│   ├── alembic/
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── api.js
│   │   ├── components/
│   │   │   ├── ContentEditor.jsx
│   │   │   ├── FormDefinitionEditor.jsx
│   │   │   ├── QRCard.jsx
│   │   │   └── formDefinitionUtils.js
│   │   └── pages/
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Axios, React Router, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy |
| Authentication | JWT, Passlib / bcrypt |
| Database | SQLite, PostgreSQL |
| Migrations | Alembic |
| QR | qrcode, Pillow |
| AI Security | Python, FastAPI, heuristic URL analysis |
| Deployment | Render |

---

## Content Model

DynamicQR-AI uses a versioned content model.

| Field | Purpose |
|---|---|
| `qr_code_id` | Parent QR code |
| `content_type` | `URL`, `TEXT`, or `FORM` |
| `content` | Content payload |
| `version` | Per-QR version number |
| `is_published` | Current published state |
| `created_at` | Creation timestamp |

The backend keeps `QRCode.content` as a legacy URL compatibility field.

Existing URL QR codes can therefore continue to resolve even when no `ContentVersion` exists.

---

## Content Types

### URL

URLs must use:

```text
http://
https://
```

Unsafe schemes such as:

```text
javascript:
data:
file:
blob:
```

and custom schemes are rejected.

URLs are limited to 2,048 characters.

URL creation and updates are passed through the AI security engine. A result marked as dangerous is rejected by the backend.

### TEXT

TEXT content is returned as:

```text
Content-Type: text/plain; charset=utf-8
```

Text:

- Cannot be blank
- Is limited to 10,000 characters
- Is never interpreted as HTML or JavaScript

### FORM

FORM content is represented as validated JSON.

Currently supported field types:

```text
text
email
textarea
```

Forms:

- Support up to 20 fields
- Validate field names and labels
- Validate required fields
- Validate maximum lengths
- Reject arbitrary HTML
- Reject JavaScript
- Reject custom external actions
- Use escaped dynamic values
- Use a restrictive Content Security Policy

The current FORM implementation is **display-only**. It does not currently submit or store responses.

---

## Authentication & Authorization

The backend provides:

```text
POST /register
POST /login
```

Login returns a JWT access token.

Authenticated QR management includes:

```text
GET  /my-qrs
GET  /details/{qr_id}
PUT  /update-qr/{qr_id}
```

Public QR resolution remains unauthenticated:

```text
GET /q/{qr_id}
```

QR ownership is enforced for authenticated management operations.

Anonymous QR creation is also supported.

---

## API

### Health

```text
GET /
GET /health
```

Health response:

```json
{
  "status": "ok"
}
```

### Create QR

```http
POST /create-qr
```

```json
{
  "content_type": "URL",
  "content": "https://example.com"
}
```

The same endpoint supports:

```text
URL
TEXT
FORM
```

The response contains the QR ID, dynamic link, QR image URL, and AI result when applicable.

### Update QR

```http
PUT /update-qr/{qr_id}
```

Example:

```json
{
  "content_type": "TEXT",
  "content": "Welcome to our event"
}
```

Each successful update creates a new content version.

### Resolve QR

```http
GET /q/{qr_id}
```

Resolution behavior:

```text
URL
 └── HTTP 302 redirect

TEXT
 └── text/plain response

FORM
 └── Safe display-only HTML
```

The resolver:

1. Finds the QR
2. Checks whether it is active
3. Increments the scan count
4. Finds the published content version
5. Dispatches according to content type

### AI Engine

```http
POST http://127.0.0.1:9000/scan?url=https://example.com
```

Example result:

```json
{
  "domain": "example",
  "risk_score": 0,
  "status": "SAFE",
  "reasons": []
}
```

The AI engine is intentionally separated from the main backend so its analysis logic can evolve independently.

---

## Security Boundaries

Current safeguards include:

- URL scheme validation
- URL length validation
- Heuristic URL risk analysis
- Plain-text TEXT responses
- FORM field allowlisting
- FORM value escaping
- Content Security Policy for FORM responses
- JWT authentication
- QR ownership checks
- Backend-authoritative validation

The frontend does not render arbitrary:

```text
HTML
JavaScript
CSS
iframes
FORM action URLs
```

The frontend also does not use `dangerouslySetInnerHTML` for user-controlled content.

The backend remains the authoritative security boundary.

### Important

DynamicQR-AI is an **MVP**, not a complete production security system.

It currently does not provide:

- Advanced URL reputation feeds
- Rate limiting
- CAPTCHA
- Managed secret infrastructure
- Enterprise abuse prevention
- Advanced ML-based URL classification
- Full production observability

The AI risk score should therefore be treated as an additional signal rather than a definitive security verdict.

---

## Deployment

The application is deployed as separate services:

```text
                    Render
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
   Frontend        Backend        AI Engine
   Static Site     Web Service    Web Service
       │              │              │
       │              ▼              │
       │          PostgreSQL         │
       │                             │
       └────────────── User ─────────┘
```

### Production Services

- Frontend: https://dynamicqr-frontend.onrender.com
- Backend: https://dynamicqr-ai.onrender.com
- AI Engine: https://dynamicqr-ai-engine.onrender.com

The frontend communicates with the backend through `VITE_API_URL`.

The backend communicates with the AI engine through `AI_ENGINE_URL`.

The database connection is configured through `DATABASE_URL`.

---

## Environment Variables

### Backend

| Variable | Local default | Purpose |
|---|---|---|
| `ENVIRONMENT` | `development` | Runtime environment |
| `DATABASE_URL` | `sqlite:///./qr_codes.db` | Database connection |
| `JWT_SECRET` | Development fallback | JWT signing secret |
| `AI_ENGINE_URL` | `http://127.0.0.1:9000` | AI engine base URL |
| `CORS_ORIGINS` | Local frontend origins | Allowed frontend origins |
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Base URL used in generated QR links |

### Frontend

| Variable | Local default | Purpose |
|---|---|---|
| `VITE_API_URL` | `http://127.0.0.1:8000` | Backend API URL |

Production secrets and deployment-specific values should be configured through the deployment platform rather than committed to source control.

---

## Local Development

### Prerequisites

- Python 3.12
- Node.js
- npm
- Git

### Backend

```powershell
cd backend
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

If you need a new environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Start AI Engine

```powershell
cd ai-engine
..\backend\venv\Scripts\python.exe -m uvicorn main:app --reload --port 9000
```

AI Engine:

```text
http://127.0.0.1:9000
```

### Start Backend

Open another terminal:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

### Start Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Testing

Backend tests:

```powershell
python -m pytest
```

Syntax validation:

```powershell
python -m compileall .
```

Frontend lint:

```powershell
cd frontend
npm run lint
```

Frontend production build:

```powershell
npm run build
```

Current backend test result:

```text
10 passed
```

---

## Roadmap

### Near Term

- Improve dashboard UX
- Version history UI
- Rollback to previous versions
- Better scan analytics
- Scheduled publishing
- Content preview
- Stronger URL security analysis

### Product Expansion

- Image content
- Poster content
- PDF content
- Video content
- Private QR codes
- Verified access
- Form submissions
- Response storage
- Email integrations
- Webhooks

### Platform

- Multi-tenancy
- Rate limiting
- CAPTCHA
- Billing
- Administrative tooling
- Better observability
- Production-grade abuse prevention
- Advanced reputation and ML-based security analysis

---

## Product Direction

The long-term idea is larger than simply generating QR codes.

The QR is the stable physical interface.

The platform behind it becomes the programmable layer that controls what the QR serves.

```text
                    ONE QR
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
         URL         TEXT        FORM
          │           │           │
          └───────────┼───────────┘
                      ▼
                Future Content
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
        Image        PDF         Video
          │           │           │
          └───────────┼───────────┘
                      ▼
                Access Control
                      │
                      ▼
                   Analytics
                      │
                      ▼
             Security Intelligence
```

The objective is to make physical QR infrastructure as flexible as a web application.

---

## Why This Project Is Technically Interesting

DynamicQR-AI is intentionally built as more than a QR generator.

The project explores several engineering problems together:

- Stable identifiers for mutable content
- Versioned content resolution
- Backward compatibility
- Authentication and ownership
- Safe rendering of user-defined forms
- Service-to-service AI integration
- SQLite → PostgreSQL deployment
- API and frontend separation
- Security-aware content validation
- Incremental architecture that can evolve into a SaaS product

The core design principle is:

> **Keep the physical QR stable. Make the software behind it changeable.**

---

## Author

**Prashant Kumar**



GitHub: https://github.com/prashantVerse12

---

## License

License and contribution terms are defined by the repository configuration.
