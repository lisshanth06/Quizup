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
- `models.py` - OTP model
- `views.py` - OTP send/verify views
- `urls.py` - Account URLs
- `admin.py` - (No admin)
- `apps.py` - App configuration
- `migrations/__init__.py`

#### 3. Quizzes App (`quizzes/`)
- `__init__.py`
- `models.py` - Quiz, Round, Question, Participant models
- `views.py` - Quiz detail, submit answer views
- `urls.py` - Quiz URLs
- `admin.py` - (No admin)
- `apps.py` - App configuration
- `migrations/__init__.py`

#### 4. Attempts App (`attempts/`)
- `__init__.py`
- `models.py` - Attempt model
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
- `accounts/send_otp.html` - OTP send form
- `accounts/verify_otp.html` - OTP verification form
- `quizzes/quiz_detail.html` - Quiz taking interface
- `quizzes/quiz_waiting.html` - Waiting page
- `leaderboard/round_leaderboard.html` - Round leaderboard
- `leaderboard/final_podium.html` - Final podium
- `dashboard/login.html` - Admin login
- `dashboard/dashboard.html` - Admin dashboard
- `dashboard/quiz_manage.html` - Quiz management
- `dashboard/round_detail.html` - Round management
- `dashboard/round_leaderboard.html` - Admin leaderboard view

### Static Files (`static/`)
- `css/style.css` - Main stylesheet

### Media Files (`media/`)
- Created automatically for question images

## Database Models

1. **OTP** (accounts)
   - email, otp_code, created_at, is_used, quiz

2. **Quiz** (quizzes)
   - name, status, created_at, updated_at, slug

3. **Round** (quizzes)
   - quiz, round_no, qualification_limit, is_active, started_at, ended_at

4. **Question** (quizzes)
   - round, text, image, option_a/b/c/d, correct_option, time_limit, order

5. **Participant** (quizzes)
   - quiz, name, email, verified, joined_at

6. **Attempt** (attempts)
   - participant, round, question, selected_option, is_correct, time_taken, created_at

## Key Features Implemented

✅ PostgreSQL database configuration
✅ Email OTP verification system
✅ Multi-round quiz system
✅ Admin dashboard (custom, no Django admin)
✅ Leaderboard with CSV export
✅ Final podium celebration
✅ Security features (no copy/paste, right-click disabled)
✅ Server-side time enforcement
✅ College email validation
✅ HTMX integration ready
✅ Responsive CSS design
✅ Database indexes for performance
✅ Optimized queries (select_related, prefetch_related)

## Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Create PostgreSQL database
3. Copy `.env.example` to `.env` and configure
4. Run migrations: `python manage.py makemigrations && python manage.py migrate`
5. Run server: `python manage.py runserver`

## Admin Access

- URL: `/dashboard/login/`
- Password: `admin123` (change in production!)

## Testing Flow

1. Admin creates quiz
2. Admin adds rounds and questions
3. Admin deploys quiz
4. Quiz appears on landing page
5. User joins with college email
6. User verifies OTP
7. User answers questions when round is active
8. Leaderboard shows after round completion
9. Admin can download CSV
10. Final podium shows top 3 after quiz ends
