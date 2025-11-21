# Library Management System API

A RESTful API for managing a mini library system, built with Django and Django REST Framework.

## Features

- **Authentication**: Token-based authentication for administrators
- **Book Management**: Full CRUD operations for books
- **Member Management**: Full CRUD operations for library members
- **Borrowing System**: Borrow and return books functionality
- **Standardized API Responses**: All responses follow a consistent format
- **API Documentation**: Interactive OpenAPI documentation with Swagger UI

## Tech Stack

- **Framework**: Django 5.2.8
- **API**: Django REST Framework 3.16.1
- **Database**: SQLite (default, configurable)
- **Authentication**: Token-based (rest_framework.authtoken)
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **Testing**: pytest, pytest-django
- **CORS**: django-cors-headers

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- virtualenv

### Installation

1. **Clone the repository**:
   ```bash
   cd /run/media/satoru/SOFTWARE/python/library-mini-system
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**:
   ```bash
   cd backend
   python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/api/`

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Administrator login

### Books
- `GET /api/books/` - List all books
- `POST /api/books/` - Create a new book
- `GET /api/books/{id}/` - Retrieve a book
- `PUT /api/books/{id}/` - Update a book
- `PATCH /api/books/{id}/` - Partial update a book
- `DELETE /api/books/{id}/` - Delete a book
- `POST /api/books/{id}/borrow/` - Borrow a book
- `POST /api/books/{id}/return_book/` - Return a book

### Members
- `GET /api/members/` - List all members
- `POST /api/members/` - Create a new member
- `GET /api/members/{id}/` - Retrieve a member
- `PUT /api/members/{id}/` - Update a member
- `PATCH /api/members/{id}/` - Partial update a member
- `DELETE /api/members/{id}/` - Delete a member

## Response Format

All API responses follow a standardized format:

### Success Response
```json
{
  "code": 200,
  "status": "OK",
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "code": 400,
  "status": "BAD REQUEST",
  "data": {
    "error": [
      "Error message 1",
      "Error message 2"
    ]
  }
}
```

## Authentication

The API uses token-based authentication. To authenticate:

1. **Login** to get a token:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "your-password"}'
   ```

2. **Use the token** in subsequent requests:
   ```bash
   curl -X GET http://127.0.0.1:8000/api/books/ \
     -H "Authorization: Token YOUR_TOKEN_HERE"
   ```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://127.0.0.1:8000/api/schema/swagger-ui/`
- ReDoc: `http://127.0.0.1:8000/api/schema/redoc/`
- OpenAPI Schema: `http://127.0.0.1:8000/api/schema/`

## Testing

Run the test suite:

```bash
cd backend
pytest
```

Run tests with coverage:

```bash
pytest --cov=api --cov-report=html
```

Run specific test file:

```bash
pytest api/tests/test_auth.py -v
```

## Project Structure

```
library-mini-system/
├── backend/
│   ├── api/
│   │   ├── migrations/
│   │   ├── tests/
│   │   │   ├── test_auth.py
│   │   │   ├── test_books.py
│   │   │   ├── test_members.py
│   │   │   └── test_borrow.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── renderers.py
│   │   └── exceptions.py
│   ├── project/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   └── pytest.ini
├── specs/
│   └── 001-library-management-apis/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── data-model.md
│       ├── research.md
│       └── quickstart.md
├── venv/
├── requirements.txt
└── README.md
```

## Development

### Settings

The project uses split settings:
- `project/settings/base.py` - Base settings
- `project/settings/development.py` - Development settings (default)
- `project/settings/production.py` - Production settings

To use production settings:
```bash
export DJANGO_SETTINGS_MODULE=project.settings.production
```

### Code Quality

The project follows Django and DRF best practices:
- Custom renderer for standardized responses
- Custom exception handler for consistent error formatting
- Token-based authentication
- Comprehensive test coverage
- API documentation with OpenAPI 3.0

## License

This project is part of a learning exercise and is provided as-is.

## Contributing

This is a mini project for demonstration purposes. For suggestions or improvements, please create an issue.
