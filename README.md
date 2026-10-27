# MealMuse

A Flask app that suggests meals based on what ingredients you have at
home, your budget, and your dietary goal. See the full SRS document
for the background, requirements, and design decisions behind this
project.

## Running it locally

```bash
pip install -r requirements.txt
python app.py          # creates mealmuse.db and starts the server
python seed.py          # (optional, in a second terminal) adds sample meals
```

Then open http://127.0.0.1:5000

## Running the tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

## Using the AI chatbox

The `/chat` page works without any setup - it just falls back to the
rule-based suggestions. To actually use an AI model, set an API key
before starting the app:

```bash
export OPENAI_API_KEY=your-key-here
python app.py
```

## Deploying it (e.g. on Render)

1. Push this project to a GitHub repository.
2. Create a new "Web Service" on Render and connect it to that repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app` (already set in the `Procfile`)
5. Add environment variables in Render's dashboard if needed:
   - `OPENAI_API_KEY` - to enable the AI chatbox
   - `SECRET_KEY` - any random string, for production
   - `DATABASE_URL` - leave unset to keep using SQLite, or point it at
     a PostgreSQL database if you need multiple users at once

## Project structure

```
app.py          - routes
config.py       - settings, read from environment variables
models.py       - database tables
services.py     - rule-based meal matching (the AI fallback)
ai_service.py   - AI chatbox integration
seed.py         - adds sample meals for testing
templates/      - HTML pages
static/         - CSS
tests/          - pytest test suite
```
