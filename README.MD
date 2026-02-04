# Not Another Hero's Book

This project follows a microservice architecture where Flask acts as a headless content API and Django acts as the gameplay engine and user-facing application.

<!-- Always mention what is unique to project compared to a typical project using your tech stack --> 
## Project Structure
```
├── /django_app            <-- Django App
│
├── /flask-api             <-- Backend API
│   ├── run.py             <-- Entry point (replaces old app.py execution)
│   ├── config.py          <-- Kept in root for easy access
│   ├── .env               <-- For secrets/API keys later
│   │
│   └── /app               <-- The actual application package
│       ├── __init__.py    <-- The "Factory" that creates the app
│       ├── extensions.py  <-- Initializes DB (fixes circular imports)
│       ├── models.py      
│       └── routes.py      <-- Endpoints (formerly in app.py)
│
└── README.md
```

my own notes (sultan):
## Flask comms
``` bash
python -m venv venv
venv\Scripts\activate
pip install flask flask-sqlalchemy flask-cors
```
