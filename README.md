# CodeAlpha URL Shortener

A beginner-friendly URL shortener built with Python, Django, SQLite, Django templates, Bootstrap 5, CSS, and JavaScript. Paste a long HTTP or HTTPS address to create a random short code. Opening that short link redirects to the saved destination and increments its click count.

## Architecture

```text
Browser (HTML form / link)
        │
        ▼
config/urls.py ── routes to ──► shortener/urls.py
                                      │
                                      ▼
                              shortener/views.py
                               │             │
                    ShortURLForm            ShortURL model
                     validates data           │
                               │               ▼
                               └──────────► SQLite via Django ORM
                                      │
                                      ▼
                           Django template response
```

### Request flow

1. The browser submits the homepage form with an HTTP `POST`. The form includes Django's CSRF token.
2. Django checks `config/urls.py`, includes the app routes from `shortener/urls.py`, then calls the matching view.
3. The `home` view binds the request data to `ShortURLForm`. The form checks that the value is a complete HTTP or HTTPS URL.
4. `create_short_url` generates a random eight-character code and saves the URL, code, timestamp, and initial click count through the `ShortURL` model. Django ORM writes the row to SQLite.
5. The dashboard renders the resulting short address with a copy button. When someone opens it, Django looks up the code from the route, increments `click_count` using an ORM expression, and sends an HTTP redirect to the destination stored in the database.

## Project structure

```text
CodeAlpha_Task1/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shortener/
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── static/shortener/
│   │   ├── css/styles.css
│   │   └── js/app.js
│   ├── templates/shortener/
│   │   ├── partials/url_table.html
│   │   ├── 404.html
│   │   ├── base.html
│   │   ├── home.html
│   │   └── url_list.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## Features

- Validate complete HTTP and HTTPS URLs before saving.
- Generate unique, random eight-character codes with collision retries and a database uniqueness constraint.
- Redirect through a saved database record; the request cannot provide a separate redirect destination.
- Count visits atomically with a Django ORM `F()` expression.
- Paginate the URL dashboard, copy links to the clipboard, and delete links using CSRF-protected `POST` forms.
- Use a custom 404 page, Django admin registration, and responsive Bootstrap 5 styling.
- Store local records in SQLite. No account or external backend service is needed.

## Requirements

- Python 3.10 or later.
- Internet access in the browser to load Bootstrap 5 from jsDelivr. The application backend itself uses only Django and SQLite.

## Installation and setup

Commands below use PowerShell on Windows. The equivalent macOS/Linux activation command is shown after the Windows block.

```powershell
# From the project folder
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. On macOS/Linux, use `python3 -m venv .venv` and `source .venv/bin/activate`.

### Database migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

The initial migration is included. `makemigrations` checks for model changes and normally reports that there is nothing new to create.

### Start the development server

```powershell
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser. The all-links table is also available at `/urls/`. Optional Django admin access is at `/admin/`; create an administrator with `python manage.py createsuperuser`.

For a deployment, provide a private `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=false`, and set `DJANGO_ALLOWED_HOSTS` to the hostnames serving the site. The checked-in fallback key and debug setting are for local learning only.

## Usage

1. Enter a complete address such as `https://www.example.com/articles/django`.
2. Select **Create short link**. The generated link appears above the dashboard and is also saved in the table.
3. Select **Copy** to copy a short link. The browser may ask for clipboard permission outside localhost or HTTPS.
4. Open the short link in a new tab to visit the saved destination. Its click count increases by one.
5. Use **All links** to browse pages of saved links. Select **Delete** to remove a record.

## Tests

The test suite covers code format and collision handling, valid and invalid forms, successful creation, redirect behavior, click counting, an unknown code, and POST-only deletion.

```powershell
python manage.py test
```

## Screenshots

Add screenshots after running the app. Suggested files:

- `docs/screenshots/dashboard.png` — creation form and recent links.
- `docs/screenshots/all-links.png` — paginated URL management table.
- `docs/screenshots/not-found.png` — custom 404 page.

## GitHub publishing

The project repository is `ArijitPan15/CodeAlpha_Task1`. If you are setting up the repository manually, use:

```powershell
git init -b main
git add .
git commit -m "Build Django URL shortener"
git remote add origin https://github.com/ArijitPan15/CodeAlpha_Task1.git
git push -u origin main
```

The local SQLite database is ignored by `.gitignore`; migrations are committed so each clone can create its own database with `python manage.py migrate`.

## 2–3 minute demo video script

**0:00–0:20 — Introduction**  
“Hi, this is my CodeAlpha URL Shortener, built with Django and SQLite. It turns long web addresses into short links and tracks visits.”

**0:20–0:50 — Create a link**  
Show the dashboard, paste a long HTTPS URL, and select **Create short link**. Point out the generated code, the copy action, and the new row in the table.

**0:50–1:20 — Redirect and analytics**  
Open the short link in a new tab. Return to the dashboard and refresh to show that the click count increased. Explain that the view looks up the code and destination in SQLite before redirecting.

**1:20–1:45 — Validation and management**  
Try an invalid address and show the form error. Open **All links**, point out the date and click count, then demonstrate the delete action if you are comfortable removing the sample row.

**1:45–2:20 — Implementation overview**  
Show `shortener/forms.py`, `models.py`, and `views.py`. Explain that Django validates the form, saves through the ORM, and increments visits with an atomic database expression. Mention CSRF-protected POST forms and pagination.

**2:20–2:40 — Wrap up**  
“This project helped me practice Django routing, forms, models, templates, migrations, and testing. Thank you for watching.”

## Implementation file guide

- `config/settings.py` — Django apps, middleware, SQLite, timezone, and static files.
- `config/urls.py` — Admin and app route registration, plus the custom 404 handler.
- `shortener/models.py` — The `ShortURL` database table and random short-code generation.
- `shortener/forms.py` — URL input widget and HTTP/HTTPS validation.
- `shortener/services.py` — Record creation with unique-code collision retries.
- `shortener/views.py` — Create/list, redirect, click counting, delete, and 404 behavior.
- `shortener/urls.py` — Homepage, list, delete, and short-code routes.
- `shortener/templates/shortener/` — Django templates that render the responsive dashboard and messages.
- `shortener/static/shortener/` — Custom styling and clipboard behavior.
- `shortener/tests.py` — Automated tests for the core requirements.
