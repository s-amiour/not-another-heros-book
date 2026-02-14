# Not Another Hero's Book

This project follows a microservice architecture where Flask acts as a headless content API and Django acts as the gameplay engine and user-facing application.

## 🏗 Architecture

1.  **Flask (The Content Vault)**: Acts as a headless CMS and Logic API. It manages the raw data (Stories, Pages, Choices) and enforces graph topology rules (e.g., ensuring no dead ends). It is secured via API Keys.
2.  **Django (The Game Engine)**: Handles the user-facing frontend, authentication, session state, and gameplay statistics. It consumes the Flask API to render stories.

---

## 📂 Project Structure

```text
.
├── django_app/                 <-- The Frontend & Game Engine
│   ├── manage.py
│   ├── django_project/         <-- Core Django settings
│   │   ├── settings.py
│   │   └── urls.py
│   └── game/                   <-- Main App
│       ├── views.py            <-- Game logic & API consumption
│       ├── models.py           <-- User stats & Play sessions
│       ├── services.py         <-- Adapter layer for Flask API calls
│       └── templates/          <-- TailwindCSS UI
│
├── flask_api/                  <-- The Backend Content API
│   ├── run.py                  <-- Entry point (replaces old app.py)
│   ├── config.py               <-- Environment config
│   └── app/
│       ├── __init__.py         <-- App Factory
│       ├── extensions.py       <-- DB & Migration setup
│       ├── models.py           <-- Story Graph (Nodes/Edges)
│       ├── routes.py           <-- JSON Endpoints
│       └── seed.py             <-- Database populator
│
├── .env                        <-- Secrets (API Keys, DB URLs)
├── requirements.txt            <-- Python dependencies
└── README.md


## 🌟 Key Features

### 🔐 Security & Roles
* **Role-Based Access Control (RBAC)**:
    * **Readers**: Can play published stories and view their own reading history.
    * **Authors**: Can create, edit, and delete *only* their own stories. Includes a visual **Story Builder**.
    * **Admins**: Can view global stats, moderate content, and suspend stories.
* **API Security**: The Flask API is protected by a secret `X-API-KEY`. Write operations are rejected without valid credentials from the Django server.

### 🎮 Gameplay & Logic
* **Graph Validation**: Stories must pass strict structural checks (at least one branch, valid endings) before they can be published.
* **State Persistence**: Player progress is saved between sessions via Django sessions and DB.
* **Moderation System**: Admins can "Suspend" stories, instantly hiding them from the public and blocking active play sessions.

---

## 🚀 Installation & Setup

### 1. Prerequisites & Clone
Ensure you have **Python 3** and **Pipenv** installed.

```bash
# Install Pipenv if you don't have it
pip install --user pipenv

# Clone the repository
git clone [https://github.com/s-amiour/not-another-heros-book.git](https://github.com/s-amiour/not-another-heros-book.git])
cd 
### 2. Install Dependencies in Each Microservice
```bash
# Install packages from Pipfile
pipenv install

# Activate the virtual environment shell
pipenv shell

### 3. Configuration (.env)
Create a `.env` file in the root directory. This is critical for connecting the two services.
```ini
# .env

# --- SECURITY ---
# Shared secret key. Django sends this, Flask checks this.
FLASK_API_KEY=change_this_to_a_secure_random_string

# --- FLASK ---
FLASK_APP=flask_api/run.py
FLASK_ENV=development
FLASK_DATABASE_URI=sqlite:///story_content.db

# --- DJANGO ---
DJANGO_SECRET_KEY=django-insecure-key-change-me
DJANGO_DEBUG=True
FLASK_API_URL=[http://127.0.0.1:5000](http://127.0.0.1:5000)
```

### 4. Initialize Flask (Backend)
Set up the content database and seed it with demo stories.
```bash
# Navigate to flask folder
cd flask_api

# Run the seed script (creates tables + populates data)
# Ensure you are running this from the flask_api directory context
python run.py

# Return to root
cd ..
```

## 5. Initialize Django (Frontend)
Set up the user database and create an admin account.

```bash
# Navigate to django folder
cd django/djangoproject/django_app

# Run migrations (Auth, Sessions, Stats)
python manage.py migrate

# Create Admin/Superuser (for Moderation tools)
python manage.py createsuperuser

# Return to root
cd ..
```


# Running the Application
You need to run two terminal windows to start the microservices.
Terminal 1: Flask API (Port 5000)
```bash
# From project root
python flask_api/run.py
```

API will run at http://127.0.0.1:5000
Terminal 2: Django App (Port 8000)
```bash
# From project root
cd django/djangoproject
python manage.py runserver
```
App will run at http://127.0.0.1:8000
