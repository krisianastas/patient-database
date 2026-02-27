# Patient Database

## Run locally

1. Create and activate a virtual environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Create environment file:
   - `cp .env.example .env`
   - Update values as needed (especially `DJANGO_SECRET_KEY`).
3. Install dependencies:
   - `python -m pip install -r requirements.txt`
4. Apply database migrations:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
5. (Optional) Create an admin user:
   - `python manage.py createsuperuser`
6. Start the development server:
   - `python manage.py runserver`
7. Open `http://127.0.0.1:8000/` in your browser.

## Frontend (Vue SPA)

1. Install frontend dependencies:
   - `cd frontend`
   - `npm install`
2. Run the Vite dev server (proxying `/api` to Django):
   - `npm run dev`
3. Build for Django static hosting:
   - `npm run build`

## Notes

- The project uses SQLite (`db.sqlite3`) by default.
- Settings module is `src.settings` (configured in `manage.py`).
