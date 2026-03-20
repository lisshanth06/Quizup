# Quiz App CSI

A complete multi-round online quiz platform built with Django and PostgreSQL.

## Features

- 🎯 Multi-round quiz system with qualification limits
- 📧 Email OTP verification (college email only)
- 📊 Real-time leaderboard with CSV export
- 🏆 Final podium celebration (top 3)
- 🔒 Security features (no copy/paste, right-click disabled)
- 👨‍💼 Custom admin dashboard (no Django admin)
- ⚡ Optimized for 500+ concurrent users

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: PostgreSQL (psycopg2)
- **Frontend**: Django Templates, CSS, HTMX
- **Email**: SMTP (Gmail supported)

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

## Installation

### 1. Clone/Download the project

```bash
cd quiz_app_csi
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

Create a PostgreSQL database:

```sql
CREATE DATABASE quizdb;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE quizdb TO postgres;
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DB_NAME=quizdb
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Note**: For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Static Files Directory

```bash
python manage.py collectstatic --noinput
```

### 8. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Usage

### Admin Access

1. Go to `http://localhost:8000/dashboard/login/`
2. Password: `admin123` (change this in production!)

### Creating a Quiz

1. Login as admin
2. Click "Create New Quiz" and enter a name
3. Click "Manage" on the quiz
4. Add rounds with qualification limits
5. Add questions to each round
6. Click "Deploy Quiz" when ready

### Participating in a Quiz

1. Go to the landing page (`http://localhost:8000`)
2. Click "Join Quiz" on a live quiz
3. Enter your name and college email (format: 2024it0054@svce.ac.in)
4. Verify OTP sent to your email
5. Answer questions when round is active
6. View leaderboard after completing

## Project Structure

```
quiz_app_csi/
├── accounts/          # Email OTP verification
├── quizzes/           # Quiz, Round, Question models
├── attempts/          # Participant answers
├── leaderboard/       # Ranking and CSV export
├── dashboard/         # Admin UI
├── core/              # Landing page
├── templates/         # HTML templates
├── static/            # CSS and static files
└── quiz_app_csi/      # Project settings
```

## Database Models

- **Quiz**: Main quiz entity
- **Round**: Multi-round structure
- **Question**: MCQ questions with images
- **Participant**: Registered participants
- **Attempt**: Participant answers and timing
- **OTP**: Email verification codes

## Security Features

- College email validation (regex pattern)
- OTP expiry (5 minutes)
- OTP resend cooldown (60 seconds)
- One participation per email per quiz
- Server-side time enforcement
- Disabled copy/paste and right-click
- Session-based authentication

## Performance Optimizations

- Database indexes on frequently queried fields
- `select_related` and `prefetch_related` for efficient queries
- Optimized leaderboard calculations
- PostgreSQL aggregation queries

## Production Deployment

Before deploying to production:

1. Change `SECRET_KEY` in `.env`
2. Set `DEBUG=False` in `settings.py`
3. Update `ALLOWED_HOSTS`
4. Use proper authentication for admin (replace simple password check)
5. Configure proper email backend
6. Set up proper static file serving
7. Use environment variables for all sensitive data
8. Enable HTTPS
9. Set up proper database backups

## License

This project is for educational purposes.

## Support

For issues or questions, please check the code comments or Django documentation.
