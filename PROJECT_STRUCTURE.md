# Quiz App CSI - Project Structure

## Complete File List

### Root Files
- `manage.py` - Django management script
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules

### Project Configuration (`quiz_app_csi/`)
- `__init__.py`
- `settings.py` - Django settings with PostgreSQL config
- `urls.py` - Main URL configuration
- `wsgi.py` - WSGI configuration
- `asgi.py` - ASGI configuration

### Apps

#### 1. Core App (`core/`)
- `__init__.py`
- `models.py` - (No models, landing page only)
- `views.py` - Landing page view
- `urls.py` - Core URLs
- `admin.py` - (No admin)
- `apps.py` - App configuration
- `migrations/__init__.py`

#### 2. Accounts App (`accounts/`)
- `__init__.py`
- `models.py` - (No models)
- `views.py` - Login view
- `urls.py` - Account URLs
- `admin.py` - (No admin)
- `apps.py` - App configuration
- `migrations/__init__.py`

#### 3. Quizzes App (`quizzes/`)
- `__init__.py`
- `models.py` - Quiz, Question, Participant models
- `views.py` - Quiz detail, submit answer views
- `urls.py` - Quiz URLs
- `admin.py` - (No admin)
- `apps.py` - App configuration
- `migrations/__init__.py`

#### 4. Attempts App (`attempts/`)
- `__init__.py`
- `models.py` - Attempt, QuestionSession, QuizAttempt models
- `views.py` - (Empty, handled by quizzes)
- `urls.py` - (Empty)
- `admin.py` - (No admin)
- `apps.py` - App configuration
- `migrations/__init__.py`

#### 5. Leaderboard App (`leaderboard/`)
- `__init__.py`
- `models.py` - (No models, uses other apps)
- `views.py` - Leaderboard calculation, CSV export, podium
- `urls.py` - Leaderboard URLs
- `admin.py` - (No admin)
- `apps.py` - App configuration
- `migrations/__init__.py`

#### 6. Dashboard App (`dashboard/`)
- `__init__.py`
- `models.py` - (No models, uses other apps)
- `views.py` - Admin dashboard views
- `urls.py` - Dashboard URLs
- `admin.py` - (No admin)
- `apps.py` - App configuration
- `migrations/__init__.py`

### Templates (`templates/`)
- `base.html` - Base template
- `core/landing.html` - Landing page
- `accounts/login.html` - Login form
- `accounts/not_allowed.html` - Access denied page
- `quizzes/quiz_detail.html` - Quiz taking interface
- `quizzes/quiz_waiting.html` - Waiting page
- `quizzes/quiz_submitted.html` - Completion page
- `quizzes/rules.html` - Quiz rules page
- `leaderboard/quiz_leaderboard.html` - Quiz leaderboard
- `leaderboard/final_podium.html` - Final podium
- `dashboard/login.html` - Admin login
- `dashboard/dashboard.html` - Admin dashboard
- `dashboard/quiz_manage.html` - Quiz management
- `dashboard/quiz_leaderboard.html` - Admin leaderboard view
- `dashboard/live_leaderboard.html` - Admin live leaderboard view

### Static Files (`static/`)
- `css/style.css` - Main stylesheet

### Media Files (`media/`)
- Created automatically for question images

## Database Models

1. **Quiz** (quizzes)
   - name, status, created_at, updated_at, slug, show_leaderboard, is_active

2. **AllowedParticipant** (quizzes)
   - quiz, email, uploaded_at

3. **Question** (quizzes)
   - quiz, text, option_a/b/c/d, correct_option, time_limit, order

4. **Participant** (quizzes)
   - quiz, name, email, has_completed, cheat_score, joined_at

5. **Attempt** (attempts)
   - participant, quiz, question, selected_option, is_correct, time_taken, created_at

6. **QuestionSession** (attempts)
   - participant, quiz, question, order, started_at, ended_at

7. **QuizAttempt** (attempts)
   - participant, quiz, created_at

## Key Features Implemented

✅ PostgreSQL database configuration
✅ Email validation system (registered users only)
✅ Randomized question order per participant
✅ Admin dashboard (custom, no Django admin)
✅ Live Leaderboard with CSV export
✅ Final podium celebration
✅ Security features (no copy/paste, right-click disabled)
✅ Server-side time enforcement
✅ CSV upload for allowed participants and questions
✅ Database indexes for performance
✅ Optimized queries (select_related, prefetch_related)

## Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Create PostgreSQL database
3. Configure `.env` file
4. Run migrations: `python manage.py makemigrations && python manage.py migrate`
5. Run server: `python manage.py runserver`

## Admin Access

- URL: `/admin/` (defined in `dashboard/urls.py`)
- Password check in `dashboard/views.py`

## Testing Flow

1. Admin creates quiz
2. Admin uploads allowed emails and questions via CSV
3. Admin deploys and starts quiz
4. Quiz appears on landing page
5. User joins with registered email
6. User follows rules and starts quiz
7. User answers questions with server-side timing
8. Leaderboard shows after completion
9. Admin can download CSV
10. Final podium shows top 3 after quiz ends
