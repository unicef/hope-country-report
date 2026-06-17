# Docker Setup and Development

The application is containerized using Docker and Docker Compose.
The Docker Compose setup is split into two files:

- `compose.yml`: This file contains the base configuration for the production environment.
- `compose.override.yml`: This file contains the configuration for the development environment. It overrides the base configuration.

---

## 1. Running the application

### Development Environment
To run the application in a development environment:
```bash
docker compose up
```
This will start all services defined in `compose.yml` and `compose.override.yml` (the web backend, primary database, read-only HOPE database, Redis, Celery worker/beat, and Flower dashboard).

### Production Environment
To run the application in a production environment, use only the base `compose.yml` file:
```bash
docker compose -f compose.yml up
```

---

## 2. Running Django Management Commands

When running with Docker Compose, you can execute Django management commands inside the backend container.

### Execute a command
To execute any command:
```bash
docker compose run --rm backend python manage.py <command>
```

### Common Commands

*   **Create a superuser**:
    ```bash
    docker compose run --rm backend python manage.py createsuperuser
    ```
*   **Run migrations manually**:
    ```bash
    docker compose run --rm backend python manage.py migrate
    ```
*   **Introspect and sync HOPE database schema**:
    ```bash
    docker compose run --rm backend python manage.py inspect_hope --database=hope_ro --schema=public --output-file=_inspect.py
    ```
