# Videoflix Backend

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.2_LTS-darkgreen)
![DRF](https://img.shields.io/badge/DRF-REST_API-red)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![Redis](https://img.shields.io/badge/Queue-Redis-red)
![Docker](https://img.shields.io/badge/Container-Docker-blue)
![FFmpeg](https://img.shields.io/badge/Video-FFmpeg-green)
![Status](https://img.shields.io/badge/Status-In_Development-orange)

Videoflix Backend is a Django-based REST API for a Netflix-/Prime-Video-like streaming platform.

It provides user registration, e-mail activation, JWT authentication with HttpOnly cookies, password reset, protected video endpoints, automatic thumbnail generation and protected HLS video streaming.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Core Features](#core-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Local Setup](#local-setup)
- [Authentication Flow](#authentication-flow)
- [API Endpoints](#api-endpoints)
- [Video Processing](#video-processing)
- [HLS Streaming](#hls-streaming)
- [Media and Static Files](#media-and-static-files)
- [Useful Commands](#useful-commands)
- [Security Notes](#security-notes)
- [Current Status](#current-status)
- [License](#license)

---

## Project Overview

> [!NOTE]
> This backend was built as part of a portfolio and learning project. The focus is on clean API design, authentication, background processing and protected video streaming.

The backend supports the main features required for a modern streaming platform:

- account registration
- e-mail-based account activation
- secure login and logout
- JWT authentication via HttpOnly cookies
- refresh-token rotation and blacklist support
- password reset flow
- protected video list endpoint
- automatic video thumbnail generation
- automatic HLS conversion using FFmpeg
- protected HLS playlist and segment delivery

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
| Local Mail Backend | Django Console Email Backend |

---

## Core Features

### Authentication

- user registration
- account activation via e-mail token
- login with e-mail and password
- logout with refresh-token blacklist
- JWT access token stored in HttpOnly cookie
- JWT refresh token stored in HttpOnly cookie
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

### Infrastructure

- Docker Compose setup
- PostgreSQL database service
- Redis service for cache and queue handling
- RQ worker for background video processing
- Gunicorn as application server
- WhiteNoise for static file handling

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
RQ Worker
   |
   | FFmpeg
   v
Thumbnails + HLS files
```

Current local Docker services:

| Service | Purpose |
|---|---|
| `videoflix_backend` | Django backend with Gunicorn |
| `videoflix_database` | PostgreSQL database |
| `videoflix_redis` | Redis cache and queue broker |

> [!IMPORTANT]
> For local submission, the RQ worker currently runs inside the backend container. For production, the worker should run as a separate service.

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
core/
├── settings.py
├── urls.py
├── wsgi.py

accounts/
├── authentication.py
├── emails.py
├── models.py
├── serializers.py
├── tokens.py
├── views.py

video_app/
├── api/
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── apps.py
├── models.py
├── signals.py
├── tasks.py

media/
├── videos/
├── thumbnails/
└── hls/
```

---

## Environment Variables

Create a `.env` file based on `.env-template`.

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=your_admin_password
DJANGO_SUPERUSER_EMAIL=admin@example.com

SECRET_KEY=your_secret_key
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

FRONTEND_BASE_URL=http://127.0.0.1:5500

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@videoflix.local
```

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enables or disables debug mode |
| `ALLOWED_HOSTS` | Allowed backend hosts |
| `CSRF_TRUSTED_ORIGINS` | Trusted CSRF origins |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins |
| `FRONTEND_BASE_URL` | Base URL used in activation and reset e-mails |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL user |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port |
| `REDIS_HOST` | Redis host |
| `REDIS_LOCATION` | Redis cache URL |
| `REDIS_PORT` | Redis port |
| `REDIS_DB` | Redis database index |
| `EMAIL_BACKEND` | Django e-mail backend |
| `DEFAULT_FROM_EMAIL` | Sender address for system e-mails |

---

## Local Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create Environment File

```bash
cp .env-template .env
```

Then update the values inside `.env`.

### 3. Start Containers

```bash
docker compose up --build
```

The backend container runs:

```bash
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py rqworker default &
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --reload
```

### 4. Access Backend

```text
http://127.0.0.1:8000
```

### 5. Access Django Admin

```text
http://127.0.0.1:8000/admin/
```

---

## Authentication Flow

Videoflix uses JWT tokens stored in HttpOnly cookies.

| Cookie | Purpose |
|---|---|
| `access_token` | Authenticates API requests |
| `refresh_token` | Requests new access tokens |

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
http://127.0.0.1:5500/pages/auth/activate.html?uidb64=<uidb64>&token=<token>
```

The frontend extracts `uidb64` and `token`, then calls:

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
http://127.0.0.1:5500/pages/auth/password_confirm.html?uidb64=<uidb64>&token=<token>
```

The frontend extracts `uidb64` and `token`, then sends the new password to:

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
| `GET` | `/api/video/` | Get video list | Authenticated |
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

> [!IMPORTANT]
> FFmpeg must be installed inside the backend container. The RQ worker must be running, otherwise thumbnails and HLS files will not be generated.

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

## Useful Commands

### Start Project

```bash
docker compose up --build
```

### Stop Containers

```bash
docker compose down
```

### Rebuild Containers

```bash
docker compose up --build --force-recreate
```

### Create Migrations

```bash
docker compose exec videoflix_backend python manage.py makemigrations
```

### Run Migrations

```bash
docker compose exec videoflix_backend python manage.py migrate
```

### Create Superuser

```bash
docker compose exec videoflix_backend python manage.py createsuperuser
```

### Run Tests

```bash
docker compose exec videoflix_backend python manage.py test
```

### Collect Static Files

```bash
docker compose exec videoflix_backend python manage.py collectstatic --noinput
```

### Run RQ Worker Manually

```bash
docker compose exec videoflix_backend python manage.py rqworker default
```

### Open Django Shell

```bash
docker compose exec videoflix_backend python manage.py shell
```

---

## Security Notes

- JWT tokens are stored in HttpOnly cookies.
- Refresh tokens are blacklisted on logout.
- Refresh-token rotation is enabled.
- Authentication error messages are generic to avoid account enumeration.
- Video list, HLS playlists and HLS segments require authentication.
- Original uploaded videos are not intended for public access.
- Public auth endpoints intentionally disable authentication checks to avoid invalid cookies blocking access.
- `DEBUG` must be disabled in production.
- `JWT_COOKIE_SECURE` should be enabled in production.
- Production deployments should use HTTPS.

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
- HLS playlists and segments are generated after video upload.
- Thumbnails are generated automatically from uploaded videos.

---

## Current Status

Implemented:

- user registration
- e-mail activation
- login
- logout
- JWT cookie authentication
- token refresh
- refresh-token blacklist
- password reset
- protected video list
- protected HLS playlist delivery
- protected HLS segment delivery
- automatic thumbnail generation
- automatic HLS conversion

Planned production improvements:

- separate Docker service for RQ worker
- Nginx for static and media delivery
- production-ready HTTPS setup
- object storage option for media files
- extended automated test coverage

---

## License

This project is part of a backend learning and portfolio project.