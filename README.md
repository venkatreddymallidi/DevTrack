# DevTrack — Django Issue Tracking API

A minimal Django backend for engineers to register reporters and log issues. It uses **pure Python OOP classes**, stores records in two **JSON files**, and exposes GET/POST endpoints suitable for Postman testing.

## Project structure

```text
devtrack/
├── manage.py
├── requirements.txt
├── README.md
├── reporters.json
├── issues.json
├── devtrack/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── issues/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py        # BaseEntity, Reporter, Issue, CriticalIssue, LowPriorityIssue
│   ├── storage.py       # JSON persistence
│   ├── views.py         # HTTP request handlers
│   ├── urls.py          # API routes
│   └── tests.py         # OOP + Django API tests
├── postman/
│   └── DevTrack.postman_collection.json
├── scripts/
│   ├── verify_oop.py
│   └── publish_to_github.sh
└── docs/
    └── README.md       # Instructions for adding real Postman screenshots
```

## Requirements and setup

- Python 3.10 or newer
- pip
- No SQL server, migrations, or Django REST Framework required

```bash
# After downloading or cloning this project, enter its root folder:
cd devtrack

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate            # macOS / Linux
# Windows PowerShell: .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python manage.py runserver
```

The server runs at `http://127.0.0.1:8000/`. The files `reporters.json` and `issues.json` start as `[]` and are updated automatically by POST requests. Run commands from the project root.

## Endpoints

| Method | URL | Behavior |
|---|---|---|
| `POST` | `/api/reporters/` | Create a reporter. Returns **201** or a **400** validation error. |
| `GET` | `/api/reporters/` | Get all reporters. Returns **200** with a list. |
| `GET` | `/api/reporters/?id=1` | Get a reporter by ID. Returns **200** or **404**. |
| `POST` | `/api/issues/` | Create an issue; checks valid reporter ID. Returns **201** with overridden `message` or **400**. |
| `GET` | `/api/issues/` | Get all issues. Returns **200** with a list. |
| `GET` | `/api/issues/?id=1` | Get a single issue. Returns **200** or **404**. |
| `GET` | `/api/issues/?status=open` | Filter issues by `status`. Returns **200** with a list. |

Only the requested POST and GET operations are supported. No PATCH/PUT/DELETE or authentication is implemented.

### 1. Create the reporter first

**POST** `http://127.0.0.1:8000/api/reporters/` with Body → raw → JSON:

```json
{
  "id": 1,
  "name": "Alex Kim",
  "email": "alex@example.com",
  "team": "backend"
}
```

Expected response: **201 Created** with the same reporter object.

### 2. Create a critical issue

**POST** `http://127.0.0.1:8000/api/issues/` with Body → raw → JSON:

```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1
}
```

Expected **201 Created** response:

```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1,
  "message": "[URGENT] Login button not working on mobile — needs immediate attention"
}
```

**400 validation example:** Send the same request with `"title": ""`:

```json
{"error": "Title cannot be empty"}
```

**404 example:** `GET /api/issues/?id=999` when issue 999 does not exist:

```json
{"error": "Issue not found"}
```

Valid issue `status` values: `open`, `in_progress`, `resolved`, `closed`. Valid `priority` values: `low`, `medium`, `high`, `critical`. Use positive, unique integer IDs. A `reporter_id` must correspond to an existing reporter. The optional string `created_at` may be supplied; if omitted, it is absent from the response and saved record to match the assignment's example. To use the suggested timestamp manually: `str(datetime.now())`.

## OOP implementation and design decision

`BaseEntity` is an abstract class requiring `validate()` and supplying shared `to_dict()`. `Reporter` and `Issue` inherit from it. `CriticalIssue` and `LowPriorityIssue` override `describe()` to produce priority-specific messages; medium/high priorities use `Issue.describe()`. The one-to-many relationship uses `reporter_id` inside each `Issue`.

**Design decision:** I kept entity definitions (`issues/models.py`), HTTP handling (`issues/views.py`), and file operations (`issues/storage.py`) separate. This makes OOP behavior testable independently of Django, avoids duplicated JSON-handling code, and lets the storage implementation change later without rewriting entity validation or routing. The `message` is returned only in the POST response (not stored) because it is a derived description rather than part of the issue data model.

## Postman testing and screenshots

1. Open **Postman → Import** and select `postman/DevTrack.postman_collection.json`.
2. Start Django. Execute **Create reporter** first, then **Create critical issue** and **Create issue with empty title**.
3. Capture an authentic Postman screenshot showing the **201 Created** success response and a second showing the **400 Bad Request** failure response. The Postman collection includes assertions for response status and JSON fields.
4. Save the screenshots as `docs/postman-success.png` and `docs/postman-failure.png`. Commit both screenshots with your submission.

> **Verified:** The collection ran against a live Django 5.2.18 server using Newman: **9 requests and 13 assertions passed**, including real 201, 400 and 404 responses. See [`docs/newman-results.json`](docs/newman-results.json) and [`docs/validation-report.md`](docs/validation-report.md). Newman results are API evidence; the assignment's Postman UI screenshots still need to be added. See [`docs/README.md`](docs/README.md).

If you run the same POST requests again, you will receive **400 ID already exists**. Use a new ID or reset both `.json` files to `[]` while the server is stopped.

## Automated tests

Offline entity checks (no Django dependency):

```bash
python scripts/verify_oop.py
```

Django tests (**16 passed** on 2026-10-11; system check passed):


```bash
python manage.py test
python manage.py check
```

`issues/tests.py` covers OOP validation, method overriding, reporter create/list/lookup, issue creation, `status` filtering, **201**, **400**, **404**, duplicates, missing foreign reporters, optional timestamps, malformed request data and unsupported methods.

## GitHub repository

Public repository: [venkatreddymallidi/DevTrack](https://github.com/venkatreddymallidi/DevTrack).

```bash
git clone https://github.com/venkatreddymallidi/DevTrack.git
cd DevTrack
```

Follow the setup commands above to install Django and start the API.

## Run the Postman collection from the command line

With a fresh data store (`reporters.json` and `issues.json` both contain `[]`) and Django running:

```bash
npx newman run postman/DevTrack.postman_collection.json
```

## Scope and limitations

This is an educational API, not a production service. CSRF protection is bypassed for the two endpoints to simplify testing from Postman, and the demo settings use a development secret. JSON files support local, single-process testing; simultaneous writes by multiple worker processes are not coordinated. For production, use a database, authentication/authorization, safe deployment settings and explicit update endpoints.
