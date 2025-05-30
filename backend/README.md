# Namesearch.io Backend

Backend service for Namesearch.io, an AI-powered brand and domain name intelligence platform.

## Features

- RESTful API built with FastAPI
- PostgreSQL database with SQLAlchemy ORM
- Redis for caching and background tasks
- JWT authentication
- Docker and Docker Compose support
- Automated testing with pytest
- Code formatting with Black and isort
- Linting with flake8 and mypy

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended)
- PostgreSQL 14+
- Redis 7+

## Getting Started

### With Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/namesearch.io.git
   cd namesearch.io/backend
   ```

2. Copy the example environment file and update it:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. The API will be available at http://localhost:5000
   - API documentation: http://localhost:5000/api/docs
   - Alternative documentation: http://localhost:5000/api/redoc

### Without Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/namesearch.io.git
   cd namesearch.io/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   # Make sure PostgreSQL and Redis are running
   alembic upgrade head
   ```

6. Run the development server:
   ```bash
   uvicorn namesearch.main:app --reload
   ```

7. The API will be available at http://localhost:5000

## API Documentation

- Swagger UI: http://localhost:5000/api/docs
- ReDoc: http://localhost:5000/api/redoc
- OpenAPI schema: http://localhost:5000/api/openapi.json

## Development

### Code Style

We use:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

To format and check the code:

```bash
# Format code with Black and isort
black .
isort .

# Run linter
flake8

# Run type checker
mypy .
```

### Testing

Run tests with pytest:

```bash
pytest
```

With coverage:

```bash
pytest --cov=namesearch tests/
```

### Database Migrations

We use Alembic for database migrations.

1. Create a new migration:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. Apply migrations:
   ```bash
   alembic upgrade head
   ```

## Environment Variables

See `.env.example` for all available environment variables.

## License

MIT
