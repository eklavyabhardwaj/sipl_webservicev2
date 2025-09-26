# sipl_webservicev2 -- Documentation

## 1. Project Overview

**eipl_webservicev2** is a Django-based backend web service designed to
handle:

-   **Configuration** → Manages global settings of the application.\
-   **Career** → Handles job listings and applicant submissions.\
-   **Contact** → Manages contact forms and inquiries.

It exposes RESTful APIs that can be consumed by frontend applications or
third-party clients.

------------------------------------------------------------------------

## 2. System Requirements

-   **Python**: 3.8+\
-   **Django**: 3.2+\
-   **Database**: PostgreSQL / MySQL / SQLite\
-   **Package Manager**: `pip` or `pipenv`\
-   **Optional**: Redis (for caching/async tasks)

------------------------------------------------------------------------

## 3. Project Structure

    eipl_webservicev2/
    │── configsite/          # Handles global configuration
    │── career/              # Job listings & applications
    │── contact/             # Contact form submissions
    │── eipl_webservicev2/   # Main Django project settings
    │── requirements.txt     # Dependencies
    │── manage.py            # Django CLI
    └── README.md

------------------------------------------------------------------------

## 4. Setup & Installation

``` bash
# Clone repository
git clone https://github.com/eklavyabhardwaj/eipl_webservicev2.git
cd eipl_webservicev2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

------------------------------------------------------------------------

## 5. Environment Configuration

Create a `.env` file in root:

``` ini
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/eipl_db

# Email for contact form
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True
```

------------------------------------------------------------------------

## 6. Database Schema & Models

### Config App

-   **Config**
    -   `id` (PK)\
    -   `site_name`\
    -   `logo_url`\
    -   `meta_description`\
    -   `updated_at`

### Career App

-   **Job**
    -   `id` (PK)\
    -   `title`\
    -   `description`\
    -   `location`\
    -   `posted_at`\
    -   `status` (active/closed)
-   **Application**
    -   `id` (PK)\
    -   `job_id` (FK → Job)\
    -   `name`\
    -   `email`\
    -   `resume_url`\
    -   `applied_at`

### Contact App

-   **ContactMessage**
    -   `id` (PK)\
    -   `name`\
    -   `email`\
    -   `subject`\
    -   `message`\
    -   `created_at`

------------------------------------------------------------------------

## 7. API Documentation

### Base URL

    http://localhost:8000/api/

### Endpoints

####  Config

  Method   Endpoint     Description
  -------- ------------ --------------------
  GET      `/config/`   Fetch site config
  PUT      `/config/`   Update site config

####  Career

  Method   Endpoint                 Description
  -------- ------------------------ --------------------
  GET      `/careers/`              List all jobs
  GET      `/careers/{id}/`         Job details
  POST     `/careers/{id}/apply/`   Submit application

**Example -- Apply to Job**

``` json
POST /careers/5/apply/
{
  "name": "John Doe",
  "email": "john@example.com",
  "resume_url": "https://example.com/resume.pdf"
}
```

Response:

``` json
{
  "status": "success",
  "message": "Application submitted successfully"
}
```

#### 🔹 Contact

  Method   Endpoint      Description
  -------- ------------- ------------------------
  POST     `/contact/`   Submit contact message

**Example -- Contact Form**

``` json
POST /contact/
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "subject": "Support Needed",
  "message": "I am facing an issue with login."
}
```

Response:

``` json
{
  "status": "success",
  "message": "Your message has been received"
}
```

------------------------------------------------------------------------

## 8. Authentication & Security

-   APIs can be public (for careers/contact)\
-   Admin endpoints require Django admin login\
-   Optional: Use `JWT` / `TokenAuth` for secure API access

------------------------------------------------------------------------

## 9. Admin Panel Usage

Visit:

    http://localhost:8000/admin/

-   Manage configs, jobs, applications, and contact messages.\
-   Superusers can add/update/delete records.

------------------------------------------------------------------------

## 10. Testing

Run all tests:

``` bash
python manage.py test
```

With coverage:

``` bash
coverage run --source='.' manage.py test
coverage report
```

------------------------------------------------------------------------

## 11. Deployment Guide

1.  **Production Server**: Use `gunicorn` or `uwsgi`\
2.  **Reverse Proxy**: Nginx / Apache\
3.  **Static Files**: Run `python manage.py collectstatic`\
4.  **Database**: Apply migrations & set up backups\
5.  **Environment Variables**: Set `.env` securely\
6.  **SSL**: Use Let's Encrypt for HTTPS

------------------------------------------------------------------------

## 12. Contributing Guidelines

-   Fork the repo\
-   Create a feature branch\
-   Commit changes with meaningful messages\
-   Add/Update tests\
-   Submit PR

------------------------------------------------------------------------

## 13. License & Contact

**License**: Proprietary License – Permission Required

**Contact**:\
- Author: Eklavya Bhardwaj\
- GitHub: [eklavyabhardwaj](https://github.com/eklavyabhardwaj)\
- Email: eklavyabhardwaj@aol.com

------------------------------------------------------------------------
