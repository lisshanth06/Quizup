# Quiz App CSI

A complete online quiz platform built with Django and PostgreSQL, featuring randomized question ordering and secure email-based access.

## Features

- 🎯 Personalized quiz experience with randomized question order per participant
- 📧 Secure email-based entry (registered users only)
- 📊 Real-time leaderboard with CSV export
- 🏆 Final podium celebration (top 3)
- 🔒 Anti-cheat features (no copy/paste, right-click disabled, tab-switch detection)
- 👨‍💼 Custom admin dashboard (no Django admin)
- ⚡ Optimized for high concurrency

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: PostgreSQL (psycopg2)
- **Frontend**: Django Templates, CSS
- **Environment**: Decouple (.env support)

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

Create a PostgreSQL database and configure the credentials in your `.env` file.

### 5. Configure Environment Variables

Create a `.env` file in the project root based on the project settings.

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Usage

### Admin Access

1. Go to `http://localhost:8000/admin/` (or your configured dashboard URL)
2. Login with the configured admin password.

### Creating and Managing a Quiz

1. Login as admin.
2. Create a new quiz.
3. Upload allowed participant emails via CSV.
4. Upload questions via CSV or add them manually.
5. Deploy and start the quiz.

### Participating in a Quiz

1. Go to the landing page.
2. Click "Join Quiz" on an active quiz.
3. Enter your name and registered email address.
4. If allowed, you will proceed to the quiz rules and then the questions.
5. Answer questions before the timer runs out.
6. View your ranking on the leaderboard after completion.

## Project Structure

- `accounts/`: Participant authentication (email-based login)
- `quizzes/`: Core quiz management, questions, and participation
- `attempts/`: Tracking participant answers and session state
- `leaderboard/`: Scoring logic and ranking views
- `dashboard/`: Custom administrative interface
- `core/`: Landing page and global layouts

## Security Features

- Email validation against an "Allowed" list uploaded by admin.
- Server-side time enforcement for each question.
- Randomized question sequence for every participant to prevent answer sharing.
- Prevention of browser actions like right-click, copy, and paste.
- Cheat score tracking for suspicious browser behavior.

## Performance Optimizations

- Extensive use of database indexes for fast lookups.
- Bulk creation for randomized sessions and CSV uploads.
- Optimized querysets using `select_related` and `prefetch_related`.
- Efficient score calculation using PostgreSQL aggregation.

## License

This project is for educational purposes.
