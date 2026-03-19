# AI-Powered Quiz API

A production-ready REST API built with Django REST Framework that uses AI to automatically generate quiz questions.

## Live API
**Base URL:** `https://web-production-3114f.up.railway.app`
**Swagger Docs:** `https://web-production-3114f.up.railway.app/swagger/`

## Tech Stack
- **Backend:** Django 4.2 + Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT (djangorestframework-simplejwt)
- **AI Integration:** OpenRouter API (Mistral 7B)
- **Deployment:** Railway
- **Documentation:** Swagger/OpenAPI (drf-yasg)

## Architecture
```
models → serializers → services → views → urls
```
Business logic lives exclusively in the services layer.

## Features
- JWT authentication with role-based access (student/admin)
- AI-generated MCQ questions via OpenRouter
- Quiz attempt tracking with real-time scoring
- Performance analytics and history
- Pagination, filtering, rate limiting
- Swagger/OpenAPI documentation

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Login and get tokens | No |
| GET | `/api/auth/profile/` | Get user profile | Yes |
| PATCH | `/api/auth/profile/` | Update profile | Yes |
| POST | `/api/auth/change-password/` | Change password | Yes |

### Quizzes
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/quizzes/` | List published quizzes | No |
| POST | `/api/quizzes/create/` | Create quiz with AI questions | Admin |
| GET | `/api/quizzes/{id}/` | Get quiz detail | Yes |
| POST | `/api/quizzes/{id}/publish/` | Publish a quiz | Admin |
| GET | `/api/quizzes/my-quizzes/` | My created quizzes | Admin |

### Attempts
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/attempts/start/` | Start a quiz attempt | Yes |
| POST | `/api/attempts/{id}/submit/` | Submit answers | Yes |
| GET | `/api/attempts/{id}/result/` | Get attempt result | Yes |
| GET | `/api/attempts/history/` | Attempt history | Yes |

### Analytics
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/analytics/performance/` | Performance stats | Yes |
| GET | `/api/analytics/history/` | Quiz history | Yes |

## Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL
- OpenRouter API key (free at openrouter.ai)

### Installation
```bash
# Clone repository
git clone https://github.com/ROSH355/Teachedison_quiz.git
cd Teachedison_quiz

# Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your values in .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Environment Variables
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=quiz_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
OPENROUTER_API_KEY=your-openrouter-key
AI_MODEL=mistralai/mistral-7b-instruct:free
```

## Database Schema
```
User (custom auth model)
 └── Quiz (created_by → User)
      └── Question (quiz → Quiz)

Attempt (user → User, quiz → Quiz)
 └── AttemptAnswer (attempt → Attempt, question → Question)

UserAnalytics (user → User, OneToOne)
```

## Key Design Decisions
- **Custom User Model** with email login and role-based access
- **Service layer** separates business logic from views
- **AI isolation** in `common/services/ai_service.py`
- **Atomic transactions** for quiz creation and attempt submission
- **Pre-computed scores** stored on AttemptAnswer for fast analytics
- **select_related/prefetch_related** throughout to prevent N+1 queries