# Yettey Backend

A comprehensive digital asset management backend service built with Clean Architecture principles, providing robust APIs for asset management, user authentication, authorization, and collaboration features.

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone git@gl.cloudike.io:yettey/backend/backend.git
   cd backend
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

4. **Run authorization migrations**
   ```bash
   python -m scripts.cli openfga model
   ```

5. **Start the development server**
   ```bash
   python src/main.py --port 8001
   ```

## 📋 Available Commands

### Development
- `uv sync` - Install dependencies and sync lockfile
- `python src/main.py --port 8001` - Run AMQP worker only

### Code Quality
- `ruff check --fix` - Run linter with auto-fix
- `ruff format` - Format code
- `mypy src` - Run type checking
- `pre-commit run --all-files` - Run all pre-commit hooks

### Testing
- `pytest` - Run all tests
- `pytest tests/asset/` - Run tests for specific module
- `pytest --no-fake` - Run pytest with real gateway implementations.

### Database
- `alembic upgrade head` - Apply all migrations
- `alembic revision --autogenerate -m "description"` - Generate new migration
- `alembic downgrade -1` - Rollback last migration

### CLI Tools
- `python -m scripts.cli admin --help` - Admin CLI commands
- `python -m scripts.cli openfga --help` - OpenFGA management commands
- `python -m scripts.cli clickhouse init` - Initialize ClickHouse tables from schema
- `python -m scripts.upload_sample_assets` - Upload sample assets to S3
- `python -m scripts.generate_openapi_schema` - Generate OpenAPI schema

### Billing Data Migration
- `python -m scripts.cli_tools.migrate_plans_and_features features` - Migrate features to database
- `python -m scripts.cli_tools.migrate_plans_and_features billing-periods` - Migrate billing periods to database
- `python -m scripts.cli_tools.migrate_plans_and_features tariff-plans` - Migrate tariff plans to database
- `python -m scripts.cli_tools.migrate_plans_and_features all` - Migrate all billing data (features → periods → plans)

## 📊 API Documentation

- **OpenAPI/Swagger**: Available at `/docs` when running the server
- **ReDoc**: Available at `/redoc`
- **Versioned APIs**: All endpoints under `/api/v1/`


## 🏗️ Architecture

### Documentation

- **[Billing Architecture](docs/BILLING_ARCHITECTURE.md)** - Comprehensive Domain-Driven Design documentation for the billing system including all 9 billing domains, pricing models, and subscription lifecycle management

### Clean Architecture Implementation

The application follows Clean Architecture principles with a clear separation of concerns:

```
├── Domain Layer (domain/)
│   ├── Business entities, commands, and core logic
│   └── Independent of external concerns
├── Application Layer (application/)
│   ├── Use cases, interactors, and application services
│   └── Orchestrates business workflows
├── Infrastructure Layer (adapters/, controllers/)
│   ├── External interfaces, databases, HTTP controllers
│   └── Framework-specific implementations
└── Common Layer (common/)
    └── Shared utilities and cross-cutting concerns
```

### Key Patterns

- **Repository Pattern**: Gateway classes handle data persistence
- **CQRS**: Separate commands and queries with dedicated handlers
- **Result Pattern**: Explicit success/failure results instead of exceptions
- **View Pattern**: Separate read models for complex queries
- **Interactor Pattern**: Application services orchestrate business logic
- **Controller-as-Orchestrator**: HTTP controllers compose business flows

## 🔧 Technology Stack

### Core Framework
- **FastAPI** - High-performance web framework
- **SQLAlchemy 2.0** - Async ORM with PostgreSQL
- **Alembic** - Database migrations
- **Dishka** - Dependency injection

### Infrastructure
- **PostgreSQL** - Primary database
- **ClickHouse** - Analytics and usage tracking database
- **RabbitMQ** - Message broker with FastStream
- **MinIO/S3** - Object storage for assets
- **OpenFGA** - Relationship-based access control

### Authentication & Security
- **JWT** - Token-based authentication
- **OAuth2** - Google, Kakao, Naver integration
- **Argon2** - Password hashing
- **MFA** - Multi-factor authentication

### Monitoring & Observability
- **Sentry** - Error tracking
- **Prometheus** - Metrics collection
- **Structured Logging** - JSON logging with correlation IDs

### Development Tools
- **Ruff** - Fast Python linter and formatter
- **MyPy** - Static type checking
- **Pytest** - Testing framework with async support
- **Pre-commit** - Git hooks for code quality
- **UV** - Fast Python package manager
