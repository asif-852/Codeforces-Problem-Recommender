# Codeforces Problem Recommender

A full-stack web application that recommends [Codeforces](https://codeforces.com/) competitive programming problems tailored to your skill level and weak areas.

## Features

- **Personalized Recommendations** — Enter your Codeforces handle and receive 6 problems matched to your rating and skill gaps.
- **Smart Grouping** — Users are automatically classified into skill groups (A–D) based on their current rating, each with curated topic sets and difficulty ranges.
- **Weakness Detection** — For users with 200+ submissions, the system identifies your top 3 struggled topics and factors them into recommendations.
- **Recent Problem Priority** — Recommendations prefer problems from recent contests so you practice on modern problem styles.
- **REST API** — Exposes API endpoints for integration with other tools or frontends.

## How It Works

| Your Rating  | Group | Problem Ratings     | Focus Topics                                           |
|-------------|-------|---------------------|--------------------------------------------------------|
| < 1000      | A     | 800 – 1000          | Brute force, implementation, math, strings, greedy     |
| 1000 – 1199 | B     | 1100 – 1400         | Binary search, graphs, trees, DFS, geometry            |
| 1200 – 1399 | C     | 1300 – 1600         | DP, combinatorics, number theory, DSU, shortest paths  |
| 1400+       | D     | 1500 – 1800         | All topics                                             |

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.10+, Django 5.0, Django REST Framework |
| **Frontend** | React 19, Vite 8 |
| **External API** | [Codeforces API](https://codeforces.com/apiHelp) |
| **Tooling** | ESLint, python-decouple |

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              Frontend (React)                            │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │
│  │ SearchBar   │   │  UserInfo   │   │ ProblemList │   │ TopicsList  │   │
│  └──────┬──────┘   └─────────────┘   └─────────────┘   └─────────────┘   │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │ App.jsx (State Management) ──────► api.js (API Client)          │     │
│  └─────────────────────────────────────────────────────────────────┘     │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │ HTTP (Vite proxy in dev)
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          Backend (Django + DRF)                          │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │ views.py ─── Input Validation ─── Response Formatting           │     │
│  └──────────────────────────────┬──────────────────────────────────┘     │
│                                 │                                        │
│  ┌──────────────────────────────┴──────────────────────────────────┐     │
│  │                        Service Layer                            │     │
│  │  ┌──────────────────┐              ┌──────────────────┐         │     │
│  │  │ codeforces_api.py│              │  recommender.py  │         │     │
│  │  │ • Rate Limiter   │              │ • Problem Filter │         │     │
│  │  │ • Caching        │              │ • Topic Matching │         │     │
│  │  │ • API Client     │              │ • Weighted Random│         │     │
│  │  └────────┬─────────┘              └──────────────────┘         │     │
│  └───────────┼─────────────────────────────────────────────────────┘     │
└──────────────┼───────────────────────────────────────────────────────────┘
               │ Rate-limited HTTP requests
               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         Codeforces API                                   │
│  • user.info      → User profile and rating                              │
│  • user.status    → All user submissions                                 │
│  • problemset.problems → Full problem catalog (~10k problems)            │
└──────────────────────────────────────────────────────────────────────────┘
```

## Backend Engineering Concepts

This section documents the engineering patterns and practices applied in the backend that aren't visible to end users but are important for maintainability, performance, and reliability.

### 1. Service Layer Architecture

The backend follows a clean separation of concerns with a dedicated service layer:

| Layer | Responsibility | Files |
|-------|---------------|-------|
| **Views** | HTTP handling, validation, response formatting | `views.py` |
| **Services** | Business logic, external API calls | `services/*.py` |
| **Constants** | Configuration, pure utility functions | `constants.py` |

This pattern keeps views thin (~67 lines) and makes business logic independently testable.

### 2. Caching Strategy

The Codeforces problem set (~10,000 problems) is cached using Django's cache framework:

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'codeforces-recommender',
    }
}
PROBLEMSET_CACHE_TTL = 60 * 30  # 30 minutes
```

**Why 30 minutes?** The problem set only changes when new contests are added (roughly weekly), so caching avoids redundant API calls while ensuring fresh data within a reasonable window.

### 3. Rate Limiting

A custom thread-safe rate limiter prevents hitting Codeforces API rate limits:

```python
class _RateLimiter:
    def __init__(self, min_interval: float = 2.0):
        self._min_interval = min_interval
        self._last_call: float = 0.0
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            elapsed = time.monotonic() - self._last_call
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_call = time.monotonic()
```

**Key decisions:**
- `threading.Lock()` ensures thread safety in multi-threaded environments
- `time.monotonic()` prevents clock drift issues
- Module-level singleton ensures global rate limiting across all requests

### 4. Input Validation

Validation is performed on both client and server sides:

```python
# Server-side (views.py)
HANDLE_MAX_LENGTH = 24
HANDLE_PATTERN = r'^[a-zA-Z0-9_-]+$'

def validate_handle(handle):
    if not handle or not handle.strip():
        return 'Handle cannot be empty.'
    if len(handle) > HANDLE_MAX_LENGTH:
        return f'Handle must be at most {HANDLE_MAX_LENGTH} characters.'
    if not re.match(HANDLE_PATTERN, handle):
        return 'Handle can only contain letters, digits, underscores, and hyphens.'
    return None
```

Client-side validation in `SearchBar.jsx` mirrors this logic for immediate user feedback.

### 5. Error Handling & Graceful Degradation

External API calls are wrapped with comprehensive error handling:

```python
def get_user_submissions(handle: str) -> list[dict]:
    try:
        _rate_limiter.wait()
        response = requests.get(url, timeout=15)
        data = response.json()
        if data.get('status') == 'OK':
            return data['result']
    except (requests.RequestException, json.JSONDecodeError, KeyError) as exc:
        logger.error("Failed to fetch submissions: %s", exc)
    return []  # Graceful degradation: return empty list instead of crashing
```

### 6. Logging

Structured logging is used throughout the service layer:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Fetching user info for handle=%s", handle)
logger.warning("Malformed JSON response from user.info")
logger.error("Failed to fetch submissions: %s", exc)
logger.debug("Rate limiter: sleeping %.2fs", sleep_time)
```

### 7. Type Hints

Python 3.10+ type hints are used for better IDE support and documentation:

```python
def recommend_problems(
    group: str,
    solved_problems: set[tuple[int, str]],
    failed_topics: Counter[str],
    submission_count: int,
) -> list[dict[str, Any]]:
```

### 8. Environment-Based Configuration

Sensitive settings are managed via environment variables using `python-decouple`:

```python
# settings.py
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000', cast=Csv())
```

### 9. Testing Strategy

The test suite covers all layers with appropriate isolation:

| Test Module | Coverage | Techniques |
|-------------|----------|------------|
| `test_constants.py` | Group classification | Pure unit tests |
| `test_codeforces_api.py` | API client | `unittest.mock.patch`, `MagicMock` |
| `test_recommender.py` | Recommendation logic | Mocked problem set |
| `test_views.py` | API endpoints | DRF `APIClient`, mocked services |

Run tests with:
```bash
cd cf_recommender
python manage.py test
```

### 10. CORS Configuration

Cross-Origin Resource Sharing is configured for frontend development:

```python
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv(),
)
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- pip & npm

### Installation

```bash
# Clone the repository
git clone https://github.com/asif-852/Codeforces-Problem-Recommender.git
cd Codeforces-Problem-Recommender
```

**Backend setup:**

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (in cf_recommender directory)
cd cf_recommender
echo "SECRET_KEY=your-secret-key-here" > .env
echo "DEBUG=True" >> .env

# Run migrations
python manage.py migrate

# Start the backend server (http://127.0.0.1:8000)
python manage.py runserver
```

**Frontend setup** (in a separate terminal):

```bash
cd frontend

# Install dependencies
npm install

# Start the development server (http://localhost:3000)
npm run dev
```

### Usage

1. Ensure both backend and frontend servers are running.
2. Open [http://localhost:3000/](http://localhost:3000/) in your browser.
3. Enter your Codeforces handle (e.g., `tourist`).
4. Click **Get Recommendations** to receive 6 personalized problems.

## API Endpoints

| Method | Endpoint                      | Description                                    |
|--------|-------------------------------|------------------------------------------------|
| GET    | `/api/user/<handle>/`         | Returns Codeforces user profile info           |
| GET    | `/api/recommend/<handle>/`    | Returns recommended problems + topics          |

### Example Response (`/api/recommend/tourist/`)

```json
{
  "user_info": {
    "handle": "tourist",
    "rating": 3800,
    "rank": "legendary grandmaster",
    "group": "D"
  },
  "recommended_problems": [
    {
      "contestId": 1900,
      "index": "E",
      "name": "Example Problem",
      "rating": 1800,
      "tags": ["dp", "graphs"]
    }
  ],
  "important_topics": ["dp", "graphs", "..."],
  "struggle_topics": ["geometry", "fft"]
}
```

## Project Structure

```
Codeforces-Problem-Recommender/
├── cf_recommender/
│   ├── manage.py
│   ├── .env                          # Environment variables (git-ignored)
│   ├── config/                       # Django settings package
│   │   ├── settings.py               # Configuration with env-based secrets
│   │   ├── urls.py                   # Root URL routing
│   │   ├── wsgi.py                   # WSGI entry point
│   │   └── asgi.py                   # ASGI entry point
│   └── codeforces_recommender/       # Main application
│       ├── views.py                  # API views (thin layer)
│       ├── urls.py                   # App URL routing
│       ├── constants.py              # Skill groups & topic mappings
│       ├── services/
│       │   ├── codeforces_api.py     # API client + caching + rate limiting
│       │   └── recommender.py        # Recommendation algorithm
│       └── tests/                    # Test suite
│           ├── test_constants.py
│           ├── test_codeforces_api.py
│           ├── test_recommender.py
│           └── test_views.py
├── frontend/                         # React + Vite SPA
│   ├── package.json
│   ├── vite.config.js                # Dev server with API proxy
│   ├── index.html
│   └── src/
│       ├── main.jsx                  # React entry point
│       ├── App.jsx                   # Root component & state management
│       ├── App.css                   # Application styles
│       ├── api.js                    # API client with error handling
│       └── components/
│           ├── SearchBar.jsx         # Input with client-side validation
│           ├── ProblemList.jsx       # Problem cards
│           ├── UserInfo.jsx          # User profile display
│           ├── TopicsList.jsx        # Topic tags
│           ├── ErrorMessage.jsx      # Error display
│           └── Spinner.jsx           # Loading indicator
├── requirements.txt                  # Python dependencies
├── package.json                      # Root package scripts
└── README.md
```

## License

This project is open source. Feel free to use and modify it.
