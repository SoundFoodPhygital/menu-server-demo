# SoundFood Menu API

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Tests](https://github.com/SoundFoodPhygital/menu-api/actions/workflows/test.yml/badge.svg)](https://github.com/SoundFoodPhygital/menu-api/actions/workflows/test.yml)
[![Lint](https://github.com/SoundFoodPhygital/menu-api/actions/workflows/lint.yml/badge.svg)](https://github.com/SoundFoodPhygital/menu-api/actions/workflows/lint.yml)

A Flask RESTful API for managing restaurant menus. This service allows users to create, manage, and organize their restaurant menus with detailed dish attributes including taste profiles, textures, emotions, and visual characteristics.

## Features

- 🔐 JWT-based authentication
- 📋 Full CRUD operations for menus and dishes
- 🎨 Rich dish attributes (taste, texture, color, emotions)
- 👤 User isolation (users can only access their own data)
- 🛡️ Rate limiting protection
- 📊 Admin dashboard with analytics
- 🐳 Docker support

## Requirements

- Python 3.10+
- Poetry (recommended) or pip

## Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/menu-server-demo.git
cd menu-server-demo

# Install dependencies
poetry install

# Initialize the database
poetry run flask --app wsgi db upgrade

# Run the development server
poetry run flask --app wsgi run --debug
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/menu-server-demo.git
cd menu-server-demo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
flask --app wsgi db upgrade

# Run the development server
flask --app wsgi run --debug
```

### Using Docker

```bash
# Production
docker compose up -d

# Development (with hot-reload)
docker compose up dev

# Build manually
docker build -t soundfood-api --target production .
```

## Configuration

Set environment variables to configure the application:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `JWT_SECRET_KEY` | JWT signing key | `dev-jwt-secret` |
| `DATABASE_URL` | Database connection string | `sqlite:///project.db` |
| `FLASK_ENV` | Environment (`development`/`production`) | `development` |

### Caching

The API uses Flask-Caching to improve performance. By default, it uses in-memory caching (`SimpleCache`).

| Endpoint | Cache Duration | Description |
|----------|----------------|-------------|
| `GET /api/emotions` | 7 days | Emotion attributes (static data) |
| `GET /api/textures` | 7 days | Texture attributes (static data) |
| `GET /api/shapes` | 7 days | Shape attributes (static data) |

For production with multiple workers, consider using Redis:

```python
# In your configuration
CACHE_TYPE = "RedisCache"
CACHE_REDIS_URL = "redis://localhost:6379/0"
```

## API Reference

All API endpoints (except authentication and health check) require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <your_token>
```

### Health Check

#### Check API and database status

```http
GET /api/health
```

**Response (200 - Healthy):**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Response (503 - Unhealthy):**
```json
{
  "status": "unhealthy",
  "database": "disconnected"
}
```

### Authentication

#### Register a new user

```http
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "user_id": 1
}
```

#### Login

```http
POST /auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1
}
```

#### Logout

```http
POST /auth/logout
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### Get current user

```http
GET /auth/me
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "role": "user"
}
```

### Menus

#### List all menus

```http
GET /api/menus
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Lunch Menu",
    "description": "Daily lunch specials",
    "dish_count": 5
  }
]
```

#### Get a specific menu

```http
GET /api/menus/{menu_id}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "title": "Lunch Menu",
  "description": "Daily lunch specials",
  "dishes": [...]
}
```

#### Create a menu

```http
POST /api/menus
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Dinner Menu",
  "description": "Evening fine dining"
}
```

**Response (201):**
```json
{
  "message": "Menu created",
  "id": 2
}
```

#### Update a menu

```http
PUT /api/menus/{menu_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response (200):**
```json
{
  "message": "Menu updated"
}
```

#### Delete a menu

```http
DELETE /api/menus/{menu_id}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Menu deleted"
}
```

### Dishes

#### List dishes in a menu

```http
GET /api/menus/{menu_id}/dishes
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Spaghetti Carbonara",
    "description": "Classic Roman pasta",
    "section": "Primi",
    "emotions": [{"id": 1, "description": "Comfort"}],
    "textures": [{"id": 1, "description": "Creamy"}],
    "shapes": [{"id": 1, "description": "Long"}],
    "bitter": 0,
    "salty": 3,
    "sour": 1,
    "sweet": 0,
    "umami": 5,
    "fat": 4,
    "piquant": 1,
    "temperature": 4,
    "colors": ["#F5DEB3", "#FFD700"]
  }
]
```

#### Create a dish

```http
POST /api/menus/{menu_id}/dishes
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Margherita Pizza",
  "description": "Traditional Neapolitan pizza",
  "section": "Pizze",
  "bitter": 0,
  "salty": 2,
  "sour": 2,
  "sweet": 1,
  "umami": 4,
  "fat": 3,
  "piquant": 0,
  "temperature": 5,
  "color1": "#FF6347",
  "color2": "#FFFFFF",
  "color3": "#228B22",
  "emotion_ids": [1, 2],
  "texture_ids": [3],
  "shape_ids": [2]
}
```

**Response (201):**
```json
{
  "message": "Dish created",
  "id": 5
}
```

#### Update a dish

```http
PUT /api/dishes/{dish_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Dish Name",
  "salty": 4
}
```

**Response (200):**
```json
{
  "message": "Dish updated"
}
```

#### Delete a dish

```http
DELETE /api/dishes/{dish_id}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Dish deleted"
}
```

### Attributes

#### Get all emotions

```http
GET /api/emotions
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {"id": 1, "description": "Happy"},
  {"id": 2, "description": "Nostalgic"}
]
```

#### Get all textures

```http
GET /api/textures
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {"id": 1, "description": "Crunchy"},
  {"id": 2, "description": "Smooth"}
]
```

#### Get all shapes

```http
GET /api/shapes
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {"id": 1, "description": "Round"},
  {"id": 2, "description": "Square"}
]
```

### Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message description"
}
```

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Access denied to resource |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 429 | Too Many Requests - Rate limit exceeded |

## Admin Dashboard

The application includes an admin dashboard accessible at `/admin`.

### Access Requirements

- Users must have `is_admin=True` or `is_manager=True` to access the dashboard
- Admins have full CRUD access to all models
- Managers have read-only access to logs and analytics

### Creating an Admin User

Use the Flask CLI to create an admin user:

```bash
poetry run flask --app wsgi shell
```

```python
from app.models import User
admin = User.create(username="admin", password="secure_password", is_admin=True)
```

### Dashboard Features

- User management
- Menu and dish overview
- Request logs and analytics
- Daily API usage charts

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_auth.py
```

### Code Formatting and Linting

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
# Check for linting issues
poetry run ruff check .

# Fix linting issues automatically
poetry run ruff check --fix .

# Format code
poetry run ruff format .

# Check formatting without making changes
poetry run ruff format --check .
```

### Database Migrations

```bash
# Create a new migration
poetry run flask --app wsgi db migrate -m "Description of changes"

# Apply migrations
poetry run flask --app wsgi db upgrade

# Rollback last migration
poetry run flask --app wsgi db downgrade
```

### Project Structure

```
menu-server-demo/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Flask extensions
│   ├── middleware.py        # Request logging middleware
│   ├── cli.py               # CLI commands
│   ├── api/
│   │   └── __init__.py      # API endpoints
│   ├── auth/
│   │   └── __init__.py      # Authentication endpoints
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── routes.py        # Admin auth routes
│   │   └── views.py         # Flask-Admin views
│   └── models/
│       ├── __init__.py
│       ├── user.py
│       ├── menu.py
│       ├── attributes.py
│       └── request_log.py
├── templates/
│   └── admin/               # Admin dashboard templates
├── migrations/              # Database migrations
├── tests/                   # Test suite
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Rate Limits

The API implements rate limiting to prevent abuse:

| Endpoint | Limit |
|----------|-------|
| Register | 5/minute |
| Login | 10/minute |
| GET endpoints | 60/minute |
| POST endpoints | 20-30/minute |
| DELETE endpoints | 10-20/minute |

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`poetry run pytest && poetry run ruff check .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request
