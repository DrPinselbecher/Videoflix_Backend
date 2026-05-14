# Videoflix Backend

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Django](https://img.shields.io/badge/Django-5.2_LTS-darkgreen)
![DRF](https://img.shields.io/badge/DRF-REST_API-red)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![Redis](https://img.shields.io/badge/Queue-Redis-red)
![Docker](https://img.shields.io/badge/Container-Docker-blue)
![FFmpeg](https://img.shields.io/badge/Video-FFmpeg-green)
![Status](https://img.shields.io/badge/Status-Ready_for_Submission-brightgreen)

Videoflix Backend is a Django-based REST API for a Netflix-/Prime-Video-like streaming platform.

It provides user registration, e-mail activation, JWT authentication with HttpOnly cookies, password reset, protected video endpoints, automatic thumbnail generation and protected HLS video streaming.

---

## Related Repositories

| Repository | Link |
|---|---|
| Backend | https://github.com/DrPinselbecher/Videoflix_Backend |
| Frontend | https://github.com/DrPinselbecher/Videoflix_Frontend |

> [!IMPORTANT]
> This repository contains only the backend. The matching frontend is maintained in a separate repository and communicates with this backend through the REST API.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Core Features](#core-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Environment Template](#environment-template)
- [Local Setup](#local-setup)
- [Authentication Flow](#authentication-flow)
- [API Endpoints](#api-endpoints)
- [Video Processing](#video-processing)
- [HLS Streaming](#hls-streaming)
- [Media and Static Files](#media-and-static-files)
- [Testing](#testing)
- [Useful Commands](#useful-commands)
- [Clean Code Structure](#clean-code-structure)
- [Security Notes](#security-notes)
- [Development Notes](#development-notes)
- [Current Status](#current-status)
- [License](#license)

---

## Project Overview

> [!NOTE]
> This backend focuses on clean API design, secure authentication, background processing and protected video streaming.

The backend supports the main features required for a modern streaming platform:

- account registration
- e-mail-based account activation
- secure login and logout
- JWT authentication via HttpOnly cookies
- CSRF protection for unsafe requests
- refresh-token rotation and blacklist support
- password reset flow
- protected video list endpoint
- automatic video thumbnail generation
- automatic HLS conversion using FFmpeg
- protected HLS playlist and segment delivery
- video list output only after completed HLS processing
- automated backend tests for authentication, video endpoints, HLS delivery, tasks and signals

The matching frontend repository is:

```text
https://github.com/DrPinselbecher/Videoflix_Frontend
```

---

## Tech Stack

| Area | Technology |
|---|---|
| Backend Framework | Django 5.2 LTS |
| API Framework | Django REST Framework |
| Authentication | djangorestframework-simplejwt |
| Database | PostgreSQL |
| Cache / Queue Broker | Redis |
| Background Jobs | django-rq |
| Video Processing | FFmpeg |
| Static Files | WhiteNoise |
| Application Server | Gunicorn |
| Containerization | Docker Compose |
| E-Mail Delivery | SMTP |
| Tests | Django TestCase / DRF APITestCase |

---

## Core Features

### Authentication

- user registration
- account activation via e-mail token
- login with e-mail and password
- logout with refresh-token blacklist
- JWT access token stored in HttpOnly cookie
- JWT refresh token stored in HttpOnly cookie
- CSRF cookie endpoint for frontend requests
- token refresh endpoint
- password reset via e-mail token
- generic authentication error messages

### Video

- protected video list endpoint
- video upload through Django Admin
- automatic thumbnail generation from uploaded videos
- automatic HLS conversion with FFmpeg
- generated 480p, 720p and 1080p HLS variants
- protected HLS playlist delivery
- protected HLS segment delivery
- video list only returns videos after HLS processing has completed

### Infrastructure

- Docker Compose setup
- PostgreSQL database service
- Redis service for cache and queue handling
- RQ worker started automatically inside the web container
- Gunicorn as application server
- WhiteNoise for static file handling
- SMTP-ready e-mail delivery

---

## Architecture

Local development setup:

```text
Frontend
   |
   | HTTP requests with credentials
   v
Django Backend / Gunicorn
   |
   | ORM
   v
PostgreSQL

Django Backend
   |
   | Queue jobs
   v
Redis
   |
   | Background processing
   v
RQ Worker Process
   |
   | FFmpeg
   v
Thumbnails + HLS files
```

Current local Docker services:

| Compose Service | Container Name | Purpose |
|---|---|---|
| `web` | `videoflix_backend` | Django backend with Gunicorn and RQ worker |
| `db` | `videoflix_database` | PostgreSQL database |
| `redis` | `videoflix_redis` | Redis cache and queue broker |

> [!IMPORTANT]
> The current Docker setup starts the RQ worker inside the web container through `backend.entrypoint.sh`.

Recommended production structure:

```text
web      -> Gunicorn
worker   -> python manage.py rqworker default
redis    -> Redis
db       -> PostgreSQL
nginx    -> Static/Media delivery
```

---

## Project Structure

```text
.
├── .dockerignore
├── .env.template
├── .gitignore
├── backend.Dockerfile
├── backend.entrypoint.sh
├── docker-compose.yml
├── manage.py
├── README.md
├── requirements.txt
├── accounts/
│   ├── admin.py
│   ├── apps.py
│   ├── authentication.py
│   ├── emails.py
│   ├── managers.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tokens.py
│   ├── urls.py
│   ├── utils.py
│   ├── views.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── factories.py
│   │   ├── test_activation.py
│   │   ├── test_login.py
│   │   ├── test_logout.py
│   │   ├── test_password_reset.py
│   │   ├── test_register.py
│   │   └── test_token_refresh.py
│   └── __init__.py
├── core/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
└── video_app/
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── signals.py
    ├── tasks.py
    ├── utils.py
    ├── api/
    │   ├── serializers.py
    │   ├── urls.py
    │   └── views.py
    ├── tests/
    │   ├── __init__.py
    │   ├── factories.py
    │   ├── test_hls_playlist.py
    │   ├── test_hls_segment.py
    │   ├── test_signals.py
    │   ├── test_tasks.py
    │   └── test_video_list.py
    └── __init__.py
```

Generated local media files are stored under:

```text
media/
├── videos/
├── thumbnails/
└── hls/
```

> [!IMPORTANT]
> `backend.entrypoint.sh` must be included in the repository because `backend.Dockerfile` uses it as the container entrypoint.

---

## Environment Template

Create a local `.env` file based on `.env.template`.

The provided values below are suitable for local Docker development. Replace `SECRET_KEY` and all placeholder values before starting the containers.

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=adminpassword
DJANGO_SUPERUSER_EMAIL=admin@example.com

SECRET_KEY=replace_this_with_a_generated_secret_key
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=your_smtp_host
EMAIL_PORT=465
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
DEFAULT_FROM_EMAIL=Videoflix <your_email@example.com>
```

| Variable | Description |
|---|---|
| `DJANGO_SUPERUSER_USERNAME` | Initial Django admin username |
| `DJANGO_SUPERUSER_PASSWORD` | Initial Django admin password |
| `DJANGO_SUPERUSER_EMAIL` | Initial Django admin e-mail |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enables or disables debug mode |
| `ALLOWED_HOSTS` | Allowed backend hosts |
| `CSRF_TRUSTED_ORIGINS` | Trusted CSRF origins |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL user |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host inside Docker Compose |
| `DB_PORT` | PostgreSQL port |
| `REDIS_HOST` | Redis host inside Docker Compose |
| `REDIS_LOCATION` | Redis cache URL |
| `REDIS_PORT` | Redis port |
| `REDIS_DB` | Redis database index |
| `EMAIL_BACKEND` | Django e-mail backend |
| `EMAIL_HOST` | SMTP host |
| `EMAIL_PORT` | SMTP port |
| `EMAIL_HOST_USER` | SMTP username |
| `EMAIL_HOST_PASSWORD` | SMTP password |
| `EMAIL_USE_TLS` | Enables TLS |
| `EMAIL_USE_SSL` | Enables SSL |
| `DEFAULT_FROM_EMAIL` | Sender address for system e-mails |

> [!WARNING]
> Do not commit a real `.env` file. Only commit `.env.template`.

---

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/DrPinselbecher/Videoflix_Backend.git
cd Videoflix_Backend
```

### 2. Create Environment File

#### Windows PowerShell

```powershell
Copy-Item .env.template .env
```

#### macOS / Linux

```bash
cp .env.template .env
```

### 3. Generate a Django Secret Key

Generate a local secret key without special characters:

```bash
python -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(50)))"
```

Copy the generated value and replace this line in `.env`:

```env
SECRET_KEY=replace_this_with_a_generated_secret_key
```

Example:

```env
SECRET_KEY=your_generated_50_character_secret_key
```

> [!IMPORTANT]
> Do not use quotation marks around the secret key if it only contains letters and numbers.

### 4. Verify Local Docker Values

For local Docker development, these values must be set in `.env`:

```env
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
```

### 5. Start Containers

```bash
docker compose up -d --build
```

The `web` container starts through `backend.entrypoint.sh`.

On startup, the backend entrypoint:

```text
waits for PostgreSQL
runs collectstatic
runs makemigrations
runs migrate
creates the configured superuser if missing
starts the RQ worker in the background
starts Gunicorn
```

The Gunicorn process runs the Django backend:

```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --reload
```

The RQ worker is started automatically:

```bash
python manage.py rqworker default &
```

### 6. Check Container Status

```bash
docker compose ps
```

Expected running containers:

```text
videoflix_backend
videoflix_database
videoflix_redis
```

### 7. Run Django System Check

```bash
docker compose exec web python manage.py check
```

Expected result:

```text
System check identified no issues (0 silenced).
```

### 8. Run Tests

```bash
docker compose exec web python manage.py test
```

Expected result:

```text
OK
```

### 9. Access Backend

```text
http://127.0.0.1:8000
```

### 10. Access Django Admin

```text
http://127.0.0.1:8000/admin/
```

Use the superuser credentials from `.env`:

```text
Username: admin
Password: adminpassword
```

### 11. Start the Frontend

Start the matching frontend repository.

Expected local frontend URL:

```text
http://127.0.0.1:5500
```

---

## Authentication Flow

Videoflix uses JWT tokens stored in HttpOnly cookies.

| Cookie | Purpose |
|---|---|
| `access_token` | Authenticates API requests |
| `refresh_token` | Requests new access tokens |
| `csrftoken` | CSRF protection for unsafe frontend requests |

Relevant cookie settings:

```python
JWT_ACCESS_COOKIE_NAME = "access_token"
JWT_REFRESH_COOKIE_NAME = "refresh_token"
JWT_COOKIE_SECURE = not DEBUG
JWT_COOKIE_SAMESITE = "Lax"
JWT_ACCESS_COOKIE_MAX_AGE = 15 * 60
JWT_REFRESH_COOKIE_MAX_AGE = 7 * 24 * 60 * 60
```

Public authentication views use:

```python
authentication_classes = []
permission_classes = [AllowAny]
```

This prevents invalid or expired cookies from blocking login, registration, activation or password reset requests.

### CSRF Cookie

The frontend requests a CSRF cookie from:

```text
GET /api/csrf/
```

Unsafe requests such as `POST` then send the CSRF token as request header:

```text
X-CSRFToken
```

### Registration

The user registers with:

```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "confirmed_password": "securePassword123"
}
```

The account is created as inactive:

```python
is_active = False
```

The user receives an activation e-mail.

### E-Mail Activation

The activation e-mail points to the frontend:

```text
http://127.0.0.1:5500/pages/auth/activate.html?uid=<uidb64>&token=<token>
```

The frontend extracts `uid` and `token`, then calls:

```text
GET /api/activate/<uidb64>/<token>/
```

Successful response:

```json
{
  "message": "Account successfully activated."
}
```

### Login

The API login uses:

```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

After a successful login, the backend sets `access_token` and `refresh_token` as HttpOnly cookies.

### Password Reset

The password reset e-mail points to the frontend:

```text
http://127.0.0.1:5500/pages/auth/confirm_password.html?uid=<uidb64>&token=<token>
```

The frontend extracts `uid` and `token`, then sends the new password to:

```text
POST /api/password_confirm/<uidb64>/<token>/
```

Example request body:

```json
{
  "new_password": "newSecurePassword123",
  "confirm_password": "newSecurePassword123"
}
```

---

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| `GET` | `/api/csrf/` | Set CSRF cookie | Public |
| `POST` | `/api/register/` | Register new user | Public |
| `GET` | `/api/activate/<uidb64>/<token>/` | Activate user account | Public |
| `POST` | `/api/login/` | Login user | Public |
| `POST` | `/api/logout/` | Logout user and blacklist refresh token | Public |
| `POST` | `/api/token/refresh/` | Refresh access token | Public |
| `POST` | `/api/password_reset/` | Request password reset e-mail | Public |
| `POST` | `/api/password_confirm/<uidb64>/<token>/` | Set new password | Public |

### Video Endpoints

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| `GET` | `/api/video/` | Get processed video list | Authenticated |
| `GET` | `/api/video/<movie_id>/<resolution>/index.m3u8` | Get HLS playlist | Authenticated |
| `GET` | `/api/video/<movie_id>/<resolution>/<segment>` | Get HLS segment | Authenticated |

Supported HLS resolutions:

```text
480p
720p
1080p
```

---

## Video Processing

Videos are uploaded through Django Admin.

Processing flow:

```text
Admin uploads video
        |
        v
Video model is saved
        |
        v
post_save signal is triggered
        |
        v
transaction.on_commit() enqueues RQ job
        |
        v
RQ worker starts FFmpeg processing
        |
        v
Thumbnail is generated
        |
        v
HLS variants are generated
        |
        v
Video instance is updated
```

Generated thumbnail:

```text
media/thumbnails/video_<id>.jpg
```

Generated HLS structure:

```text
media/hls/<video_id>/
├── master.m3u8
├── 480p.m3u8
├── 480p_00000.ts
├── 720p.m3u8
├── 720p_00000.ts
├── 1080p.m3u8
└── 1080p_00000.ts
```

The video list endpoint only returns videos after HLS processing has completed.

> [!IMPORTANT]
> FFmpeg must be installed inside the backend image. The RQ worker must be running, otherwise thumbnails and HLS files will not be generated.

---

## HLS Streaming

HLS playlists and segments are protected through Django API views.

Playlist response content type:

```text
application/vnd.apple.mpegurl
```

Segment response content type:

```text
video/MP2T
```

Segment validation prevents invalid file access:

```text
segment must end with ".ts"
segment must not contain "/" or "\"
segment must start with the selected resolution prefix
```

Valid example:

```text
/api/video/1/720p/720p_00000.ts
```

Invalid examples:

```text
/api/video/1/720p/../secret.ts
/api/video/1/720p/480p_00000.ts
/api/video/1/720p/file.mp4
```

---

## Media and Static Files

### Development

In development, media files are served by Django when `DEBUG=True`.

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Example thumbnail URL:

```text
http://127.0.0.1:8000/media/thumbnails/video_1.jpg
```

### Production

Recommended production setup:

| File Type | Recommended Delivery |
|---|---|
| Static files | WhiteNoise or Nginx |
| Thumbnails | Nginx or Object Storage |
| HLS playlists and segments | Protected Django API or secured Nginx |
| Original videos | Not publicly exposed |

> [!WARNING]
> Original uploaded videos should not be publicly exposed in production.

---

## Testing

The backend includes automated tests for authentication, video endpoints, HLS delivery, background tasks and Django signals.

Run all tests:

```bash
docker compose exec web python manage.py test
```

Run only account tests:

```bash
docker compose exec web python manage.py test accounts
```

Run only video app tests:

```bash
docker compose exec web python manage.py test video_app
```

Test coverage includes:

- user registration
- account activation
- login
- logout
- token refresh
- password reset
- password confirmation
- protected video list
- protected HLS playlist delivery
- protected HLS segment delivery
- video processing task
- video model signals

---

## Useful Commands

### Start Project

```bash
docker compose up --build
```

### Start Project in Background

```bash
docker compose up -d --build
```

### Stop Containers

```bash
docker compose down
```

### Reset Containers and Volumes

```bash
docker compose down -v
docker compose up -d --build
```

### Rebuild Containers

```bash
docker compose up --build --force-recreate
```

### Create Migrations

```bash
docker compose exec web python manage.py makemigrations
```

### Run Migrations

```bash
docker compose exec web python manage.py migrate
```

### Check Django Project

```bash
docker compose exec web python manage.py check
```

### Create Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### Run Tests

```bash
docker compose exec web python manage.py test
```

### Collect Static Files

```bash
docker compose exec web python manage.py collectstatic --noinput
```

### Open Django Shell

```bash
docker compose exec web python manage.py shell
```

### Show Backend Logs

```bash
docker compose logs web --tail=100
```

### Show Extended Backend Logs

```bash
docker compose logs web --tail=300
```

### Test SMTP E-Mail Delivery

```bash
docker compose exec web python manage.py shell -c "from django.core.mail import send_mail; print(send_mail('Videoflix SMTP Test', 'Testmail erfolgreich.', None, ['your-email@example.com'], fail_silently=False))"
```

Expected result:

```text
1
```

---

## Clean Code Structure

The backend structure follows the project Definition of Done:

| File | Responsibility |
|---|---|
| `views.py` | API views that return responses |
| `serializers.py` | Request validation and response serialization |
| `services.py` | Business logic and authentication operations |
| `utils.py` | Helper functions, paths, cookies, FFmpeg helpers |
| `emails.py` | E-mail URL building and sending |
| `tasks.py` | Background job entry points |
| `signals.py` | Django model signal handlers |
| `authentication.py` | Custom cookie-based JWT authentication |

Backend-specific clean code goals:

- functions have one clear responsibility
- helper logic is moved out of views
- views mainly validate requests and return responses
- long helper logic is placed in `utils.py` or `services.py`
- variable and function names follow `snake_case`
- unused code and commented-out code are removed
- code is structured to stay PEP 8 compatible where possible

---

## Security Notes

- JWT tokens are stored in HttpOnly cookies.
- Refresh tokens are blacklisted on logout.
- Refresh-token rotation is enabled.
- CSRF protection is used for unsafe frontend requests.
- Authentication error messages are generic to avoid account enumeration.
- Video list, HLS playlists and HLS segments require authentication.
- Original uploaded videos are not intended for public access.
- Public auth endpoints intentionally disable authentication checks to avoid invalid cookies blocking access.
- `DEBUG` must be disabled in production.
- `JWT_COOKIE_SECURE` should be enabled in production.
- Production deployments should use HTTPS.
- Real secrets must not be committed to Git.
- `.env` must never be committed.
- `.env.template` must not contain production secrets.

Generic authentication error example:

```json
{
  "detail": "Bitte überprüfe deine Eingaben und versuche es erneut."
}
```

---

## Development Notes

- The project uses a custom user model in the `accounts` app.
- `username` remains a real database field.
- `email` remains a real database field.
- During registration, `username` is set to the user's e-mail address.
- Django Admin login uses `username` and `password`.
- API login uses `email` and `password`.
- The RQ worker is required for thumbnail and HLS generation.
- The RQ worker is started automatically by `backend.entrypoint.sh`.
- HLS playlists and segments are generated after video upload.
- Videos are returned by the video list endpoint only after HLS processing has completed.
- Thumbnails are generated automatically from uploaded videos.
- The frontend and backend are separate repositories.
- Frontend/backend communication happens through the REST API.
- The Docker entrypoint waits for PostgreSQL before running startup tasks.
- E-mail links use `uid` as frontend query parameter and pass the base64 encoded user ID to backend endpoints as `uidb64`.

---

## Current Status

Implemented:

- user registration
- e-mail activation
- login
- logout
- JWT cookie authentication
- CSRF cookie endpoint
- token refresh
- refresh-token blacklist
- password reset
- protected video list
- protected HLS playlist delivery
- protected HLS segment delivery
- automatic thumbnail generation
- automatic HLS conversion
- RQ worker startup through backend entrypoint
- backend clean code refactor according to DoD
- automated tests for authentication endpoints
- automated tests for video list, HLS playlists and HLS segments
- automated tests for video processing task and signals
- Docker-based local setup with PostgreSQL, Redis, Gunicorn and RQ worker
- SMTP-ready e-mail delivery configuration
- public logo URL for HTML e-mails
- frontend-compatible `uid` query parameters for activation and password reset links
- video list filtering for completed HLS processing

Planned production improvements:

- Nginx for static and media delivery
- separate production worker service
- production-ready HTTPS setup
- object storage option for media files
- extended edge-case and integration test coverage

---

## License

This project is currently not licensed for public reuse.