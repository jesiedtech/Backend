# Jesi - FastAPI Application

A FastAPI-based application with user authentication and email verification.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=postgresql://user:password@localhost/jesi
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000
API documentation will be available at http://localhost:8000/docs 

python -m app.db.migrations.run_migration