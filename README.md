# DynamicQR-AI

DynamicQR-AI is a full-stack dynamic QR platform. It generates QR images that
point to a stable backend route instead of encoding a final destination
directly. The published content behind a QR can therefore be changed without
reprinting the QR image.

The current project combines:

- A FastAPI backend for QR generation, resolution, authentication, and QR
  management.
- A React/Vite dashboard for registration, login, QR creation, and
  URL/TEXT/FORM management.
- A small FastAPI AI engine that assigns heuristic URL risk scores.
- SQLite and SQLAlchemy for local persistence.

This repository is an active development project. The sections below describe
the behavior that exists in the current source tree, not the broader product
vision.

## Current status

### Implemented

- Dynamic QR generation with stable eight-character QR IDs.
- QR image generation on demand through the backend.
- Public QR resolution at `GET /q/{qr_id}`.
- URL, TEXT, and FORM content versions in the backend.
- URL redirects, plain-text responses, and safe display-only form responses.
- URL content updates while keeping the same QR ID and image.
- Versioned content with one published version at a time.
- Legacy URL fallback from `QRCode.content`.
- Scan counting.
- User registration and login.
- Password hashing with Passlib/bcrypt.
- JWT-based protected QR management endpoints.
- Ownership checks for QR management.
- AI URL risk scoring during URL creation and URL updates.
- React dashboard with login, registration, QR listing, URL/TEXT/FORM
  creation and editing, scan counts, QR images, version information, and
  security badges.
- Multi-content dashboard integration from Phase 10D, including a structured
  FORM definition editor.

### Partially implemented

- FORM is display-only. It does not submit or store responses.
- AI analysis is a heuristic scanner, not a production reputation or machine
  learning service.
- The application is suitable for local development, not production
  deployment.

### Planned or future

The following are not implemented in the current repository:

- Public MVP deployment and real-user testing.
- Content preview and further dashboard UX refinement.
- FORM submissions, response storage, email, webhooks, or external actions.
- Version history and rollback UI.
- Scheduled publishing and expiration.
- Production secrets management, HTTPS deployment, and cloud infrastructure.
- Containerization and production observability.
- Rate limiting, CAPTCHA, multi-tenancy, billing, and administrative tooling.
- Advanced URL reputation and ML-based classification.
- Additional content types such as image, poster, PDF, and video.
- Future access-control modes such as private or verified QR codes.

## Why dynamic QR codes?

A static QR normally contains its final URL. Once printed, changing that URL
requires replacing the QR. DynamicQR-AI instead uses this flow:

```text
Printed QR image
      |
      v
GET /q/{qr_id}
      |
      v
Current published ContentVersion
      |
      +--> URL  : HTTP 302 redirect
      +--> TEXT : text/plain response
      +--> FORM : safe display-only HTML form
```

The QR ID and QR image remain stable while the published content version
changes.

## Architecture

```text
                    +----------------------+
                    | React/Vite dashboard |
                    |   localhost:5173     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | FastAPI backend      |
                    |   localhost:8000     |
                    +------+-----------+---+
                           |           |
                           v           v
                  +--------------+  +------------------+
                  | SQLite       |  | AI engine        |
                  | SQLAlchemy   |  | localhost:9000  |
                  +--------------+  +------------------+
```

| Component | Location | Technology | Local port | Responsibility |
| --- | --- | --- | ---: | --- |
| Backend | [`backend/`](./backend) | Python, FastAPI, SQLAlchemy | `8000` | API, QR lifecycle, auth, content resolution |
| Frontend | [`frontend/`](./frontend) | React, Vite, Axios | `5173` | Login, registration, dashboard, URL/TEXT/FORM management |
| AI engine | [`ai-engine/`](./ai-engine) | Python, FastAPI | `9000` | Heuristic URL risk analysis |
| Database | `backend/qr_codes.db` | SQLite | - | Users, QR codes, content versions |

## Repository structure

```text
DynamicQR-AI/
├── ai-engine/
│   ├── main.py
│   └── scanner.py
├── backend/
│   ├── auth.py
│   ├── content.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── tests/
│       └── test_content_versions.py
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
├── requirements.txt
└── README.md
```

## Content versioning

The backend keeps the existing `ContentVersion` table as the versioned
content source:

| Field | Purpose |
| --- | --- |
| `qr_code_id` | Parent QR code |
| `content_type` | `URL`, `TEXT`, or `FORM` |
| `content` | URL/text string or serialized FORM JSON |
| `version` | Per-QR version number |
| `is_published` | Identifies the current published version |
| `created_at` | Creation timestamp |

`backend/content.py` provides normalization, validation, version creation,
published-version lookup, and legacy backfill.

Phase 10D made these backend capabilities usable from the React dashboard
without changing the backend API or data model. The dashboard now selects
`URL`, `TEXT`, or `FORM` content during creation and editing, displays the
current content type and version when available, and preserves the existing
authentication, ownership, loading, error, refresh, QR image, scan, and
security-badge behavior.

### Phase 10D — Multi-Content Dashboard Integration

Phase 10D is complete in commit `1ac3358`. The implemented frontend changes
are:

- [`frontend/src/api/api.js`](./frontend/src/api/api.js): generalized create
  and update payload support for `URL`, `TEXT`, and `FORM`, while preserving
  the legacy URL helper behavior.
- [`frontend/src/pages/Dashboard.jsx`](./frontend/src/pages/Dashboard.jsx):
  URL/TEXT/FORM selection and content-aware QR creation, with existing
  authentication, loading, error, and list-refresh behavior preserved.
- [`frontend/src/components/QRCard.jsx`](./frontend/src/components/QRCard.jsx):
  content type display, version information with an unavailable fallback,
  type-aware editing, defensive FORM parsing, and preservation of existing
  QR, security, scan, image, and public-link information.
- [`frontend/src/components/ContentEditor.jsx`](./frontend/src/components/ContentEditor.jsx):
  shared URL/TEXT/FORM content editor.
- [`frontend/src/components/FormDefinitionEditor.jsx`](./frontend/src/components/FormDefinitionEditor.jsx):
  structured FORM editor for title, submit label, field name, field label,
  field type, required state, maximum length, and adding or removing fields.
- [`frontend/src/components/formDefinitionUtils.js`](./frontend/src/components/formDefinitionUtils.js):
  shared FORM utilities including `DEFAULT_FIELD`, `createDefaultForm`, and
  `parseFormContent`.

The existing URL workflow remains supported. Legacy URL create/update helpers,
existing QR IDs, authentication, ownership behavior, and dashboard flows
remain intact. The backend API was not changed during Phase 10D.

`QRCode.content` remains as a legacy URL compatibility field. If a QR has no
content version, the public resolver validates that field as an HTTP(S) URL
and redirects to it. Existing URL QR IDs therefore remain usable.

### URL

URL content is an `http://` or `https://` URL. Other schemes, including
`javascript:`, `data:`, `file:`, `blob:`, and custom schemes, are rejected.
URLs are limited to 2,048 characters. URL creation and URL updates continue to
call the AI engine; a result containing `DANGEROUS` is rejected.

### TEXT

TEXT content is returned literally as:

```text
Content-Type: text/plain; charset=utf-8
```

Blank text is rejected and text is limited to 10,000 characters. Text is not
treated as HTML or JavaScript.

### FORM

FORM content is validated JSON stored in the existing `content` string field.
The current allowlisted field types are:

- `text`
- `email`
- `textarea`

The validator limits forms to 20 fields and 50 KB. It also validates field
names, labels, required flags, and maximum lengths. Public FORM resolution
uses backend-generated markup with escaped dynamic values and a restrictive
Content Security Policy. It is display-only: there is no submission endpoint
or response storage.

## Authentication and authorization

The backend exposes registration and login endpoints. Login returns a JWT.
The frontend stores the token locally and sends it in the authorization
header for management requests.

The following management operations require an authenticated owner:

- `GET /my-qrs`
- `GET /details/{qr_id}`
- `PUT /update-qr/{qr_id}`

Public QR scanning at `GET /q/{qr_id}` does not require JWT authentication.
The create route supports anonymous creation through the optional user
dependency; authenticated creation associates the QR with the current user.

## Backend API

### Health

```text
GET /
```

Returns a simple backend/AI status payload.

### Authentication

```text
POST /register
POST /login
```

`/register` accepts an email and password. `/login` returns an access token.

### QR creation

Legacy URL-compatible request:

```text
POST /create-qr?content_url=https://example.com
```

Generalized JSON content request:

```json
{
  "content_type": "URL",
  "content": "https://example.com"
}
```

The generalized request also accepts `TEXT` content or a validated `FORM`
definition. The response includes the QR ID, dynamic link, QR image URL, and
AI result.

### QR update

Existing URL clients remain supported:

```json
{
  "destination_url": "https://example.org"
}
```

The generalized update shape is:

```json
{
  "content_type": "TEXT",
  "content": "Welcome"
}
```

FORM content is supplied as a JSON object in `content`. Each successful update
publishes a new version. URL updates also update the legacy `QRCode.content`
field and AI status fields.

### Public resolution

```text
GET /q/{qr_id}
```

Resolution is public. The backend looks up the QR, checks its active state,
increments the scan count, selects the published version, and dispatches by
content type:

- `URL`: HTTP `302` with the URL in the `Location` header.
- `TEXT`: HTTP `200` with a `text/plain` body.
- `FORM`: HTTP `200` with escaped, display-only HTML.
- No version: validated legacy URL redirect.
- Unknown published type: controlled server error.

### Authenticated QR management

```text
GET /my-qrs
GET /details/{qr_id}
PUT /update-qr/{qr_id}
```

Management responses include current content, content type, version, scan
count, active state, AI status/risk fields, QR link, and QR image where
applicable.

### AI engine

```text
GET  http://127.0.0.1:9000/
POST http://127.0.0.1:9000/scan?url=https://example.com
```

The scanner currently checks HTTPS usage, suspicious keywords, and URL length.
It returns a domain, numeric risk score, status, and reasons. The backend
uses the result for URL creation and URL updates only. AI scoring is not a
guarantee that a destination is safe.

## Environment configuration

Deployment-specific settings are read from environment variables. No
production secrets or Render service URLs are committed to this repository.

### Backend variables

| Variable | Local development value | Purpose |
| --- | --- | --- |
| `ENVIRONMENT` | `development` | Runtime environment; production enables JWT secret validation |
| `DATABASE_URL` | `sqlite:///./qr_codes.db` | SQLAlchemy database connection URL |
| `JWT_SECRET` | Development-only fallback | JWT signing secret; set a strong secret in Render |
| `AI_ENGINE_URL` | `http://127.0.0.1:9000` | AI engine base URL |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated allowed frontend origins |
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Public backend URL used in generated QR links and image URLs |

For local development, `ENVIRONMENT=development` (the default) allows the
documented development-only JWT fallback. For Render, set
`ENVIRONMENT=production` and provide a strong, unique `JWT_SECRET`; the
backend fails at startup if the secret is missing or still equals the
development fallback. Also set `DATABASE_URL`, `AI_ENGINE_URL`,
`CORS_ORIGINS`, and `PUBLIC_BASE_URL` in the Render service environment.
`CORS_ORIGINS` accepts multiple origins separated by commas.

`DATABASE_URL` is configurable for deployment. The backend includes Alembic
migrations and the PostgreSQL driver; run migrations before starting a
production instance:

```powershell
cd backend
.\venv\Scripts\alembic.exe upgrade head
```

Development keeps the existing SQLite `create_all()` and legacy URL backfill
convenience. Production does not run `create_all()` or automatic backfill at
startup.

QR image responses use the existing `/qr-images/{qr_id}.png` URL, but the PNG
is generated on demand instead of being persisted to the local filesystem.
This avoids relying on Render's ephemeral service filesystem.

### Frontend variable

| Variable | Local development value | Purpose |
| --- | --- | --- |
| `VITE_API_URL` | `http://127.0.0.1:8000` | Backend base URL used by Axios |

Vite reads `VITE_API_URL` at build time. Set it to the deployed backend URL
when building the frontend for Render. Do not put a production URL in source
code.

### Health endpoints

The backend and AI engine each expose an unauthenticated health endpoint:

```text
GET /health
```

The response is:

```json
{"status": "ok"}
```

These endpoints do not require JWT authentication.

## Local development

### Prerequisites

- Python 3.12 is the tested backend runtime.
- Node.js and npm.
- A local SQLite-compatible environment.

### Install backend dependencies

From the repository root:

```powershell
P:\CODING\DynamicQR-AI\backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

If the existing backend environment is unavailable, create a project-specific
environment according to your local Python workflow. Do not commit virtual
environment directories.

### Install frontend dependencies

```powershell
cd frontend
npm install
```

### Start the AI engine

From the AI engine directory:

```powershell
cd ai-engine
..\backend\venv\Scripts\python.exe -m uvicorn main:app --reload --port 9000
```

### Start the backend

In another terminal:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

The backend creates or opens `backend/qr_codes.db`. QR images are generated
on demand by the backend, so local image files are not required.

### Start the frontend

In another terminal:

```powershell
cd frontend
npm run dev
```

Open the Vite URL shown by the command, normally
`http://localhost:5173`.

## Validation commands

Backend tests:

```powershell
cd backend
..\backend\venv\Scripts\python.exe -m pytest
```

Backend syntax compilation:

```powershell
cd backend
.\venv\Scripts\python.exe -m compileall .
```

Frontend lint and build:

```powershell
cd frontend
npm run lint
npm run build
```

## Development history

The current Git history records these major milestones:

| Commit | Verified capability |
| --- | --- |
| `7b2295f` | Dynamic QR destination update foundation |
| `120edd7` | Frontend integration for dynamic QR updates |
| `f14577a` | QR ownership and authenticated management |
| `742ea26` | Frontend authentication and QR dashboard |
| `33f3436` | ContentVersion foundation and URL versioning |
| `8204539` | Multi-content public resolution |
| `bfd3418` | Project architecture and development roadmap documentation |
| `1ac3358` | Multi-content dashboard support for URL/TEXT/FORM |

These milestones describe repository history; the source tree remains the
authoritative definition of current behavior. Phase 10D is complete. Its
frontend validation was recorded as:

- `npm run lint` — PASS, 0 errors
- `npm run build` — PASS
- `python -m pytest` — PASS, 10 tests passed
- `git diff --check` — PASS

Commit `1ac3358` was pushed successfully to `origin/master`. No manual browser
testing or production deployment is claimed by this documentation.

## Security boundaries

Implemented safeguards include URL scheme validation, URL length validation,
AI URL scanning, plain-text TEXT responses, FORM field allowlisting, escaped
FORM values, and a FORM response CSP.

The project is not yet a production security system. It does not currently
provide rate limiting, a managed secret store, HTTPS deployment, advanced
reputation feeds, submission abuse controls, or a production deployment
configuration. The JWT secret and local service configuration should be
externalized before deployment.

The Phase 10D dashboard security boundary is intentionally limited:

- FORM fields are limited to `text`, `email`, and `textarea`, with a maximum
  of 20 fields.
- The frontend mirrors the backend's content and FORM constraints for user
  feedback, but the backend remains authoritative for validation and security.
- The dashboard does not accept or render arbitrary HTML, JavaScript, CSS,
  iframe content, or arbitrary FORM action URLs.
- The frontend does not use `dangerouslySetInnerHTML` and does not fetch
  arbitrary destination URLs for previews.
- Existing URL AI security behavior remains unchanged and continues through
  the backend.

## License and author

The repository currently identifies **Prashant Kumar** as the author. Consult
the repository and GitHub project settings for the applicable license and
contribution terms.
