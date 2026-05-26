# SYNTIQ — Hybrid AST Analyzer & Linguistic Humanizer

**Dual-Pipeline Architecture · Django · Python · Celery · Redis · PostgreSQL**

---

## Quick Start

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run database migrations
python manage.py migrate

# 4. Collect static files (for production)
python manage.py collectstatic

# 5. Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Architecture Overview

```
User Submission
     │
     ├── TRACK A: AST Engine (CPU · Instant)
     │   ├── ast.parse() → tree graph
     │   ├── McCabe complexity (branch counting)
     │   ├── Hazard detection (eval, exec, bare except)
     │   └── Function profiling
     │
     └── TRACK B: Linguistic Pipeline (Async · Network)
         ├── Redis queue → 202 Accepted
         ├── Celery worker → LLM API
         ├── Regex fingerprint removal
         └── Perplexity + Burstiness metrics
```

## Key Files

| File | Purpose |
|------|---------|
| `analyzer/engine.py` | Core logic: ASTAnalyzer, LinguisticHumanizer, SubmissionTracker |
| `analyzer/views.py` | Django views + REST API endpoints |
| `templates/analyzer/index.html` | Main showcase UI |
| `templates/analyzer/dashboard.html` | Analytics dashboard |
| `static/css/syntiq.css` | Professional terminal aesthetic |
| `static/js/syntiq.js` | Frontend logic, result rendering |

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET`  | `/` | Main application |
| `GET`  | `/dashboard/` | Analytics dashboard |
| `POST` | `/api/analyze/` | AST analysis only |
| `POST` | `/api/humanize/` | Text humanization only |
| `POST` | `/api/submit/` | Dual pipeline (both tracks) |
| `GET`  | `/api/stats/` | Aggregated analytics |

## Production Setup (PostgreSQL + Celery)

```python
# settings.py — switch to PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'syntiq_db',
        'USER': 'syntiq_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# settings.py — Celery + Redis
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

```bash
# Start Redis
redis-server

# Start Celery worker
celery -A syntiq worker --loglevel=info

# Start Django
gunicorn syntiq.wsgi:application
```

---

*SYNTIQ — Where code intelligence meets linguistic precision.*
