# Virtual Environment Setup and Development

It is recommended to use a virtual environment to install the project dependencies and run the application locally on your host machine.

## 1. Setup

The project uses **uv** for dependency management. Make sure you have `uv` installed before proceeding (e.g., via `curl -LsSf https://astral.sh/uv/install.sh | sh` or homebrew `brew install uv`).

### Create a virtual environment
Create a virtual environment using `uv`:
```bash
uv venv
```

### Activate the virtual environment
To activate the virtual environment:
```bash
source .venv/bin/activate
```
*(If you use `direnv` and allow the `.envrc` in the repository, the virtual environment will be automatically activated when you navigate to the project folder).*

### Install dependencies
Sync the dependencies defined in `pyproject.toml` and `uv.lock`:
```bash
uv sync
```
*(This will automatically configure the project dependencies, dev dependencies, and install the package in editable mode).*

---

## 2. Bootstrapping the Application

Before running the application for the first time, you must run migrations, load initial data (such as country shapefiles), and create an administrator user. HCR provides a custom `upgrade` command to do all of this in one step:

```bash
python manage.py upgrade --admin-email admin@unicef.org --admin-password 123
```

---

## 3. Running the Development Server

Start the Django development server:
```bash
python manage.py runserver
```
The application will be available at `http://127.0.0.1:8000`.

---

## 4. Running Celery (Background Tasks)

To process background tasks and generate reports asynchronously, start the following Celery components in separate terminal windows:

*   **Celery Worker**:
    ```bash
    celery -A hope_country_report.config.celery worker --loglevel=info
    ```
*   **Celery Beat (Scheduler)**:
    ```bash
    celery -A hope_country_report.config.celery beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ```
*   **Flower (Monitoring Dashboard)**:
    ```bash
    celery -A hope_country_report.config.celery flower
    ```
    The Flower dashboard will be available at `http://localhost:5555`.

---

## 5. Syncing the HOPE Database Schema

HCR queries the upstream read-only HOPE database. Django models representing the HOPE database schema are stored in `src/hope_country_report/apps/hope/models/_inspect.py` as unmanaged models (`managed = False`).

Whenever the upstream HOPE database schema changes, you need to regenerate these models to keep them synchronized with the database:

```bash
python manage.py inspect_hope --database=hope_ro --schema=public --output-file=_inspect.py
```

### Options
- `--database`: The database alias from Django settings to introspect (defaults to `hope_ro`).
- `--schema`: The database schema to introspect (defaults to `public`).
- `--output-file`: The output file name, relative to `src/hope_country_report/apps/hope/models/` (defaults to `_inspect.py`).

The command will automatically introspect the database tables in the selected schema, filter them, write the definitions, and run `ruff format` to auto-format the generated code.

---

## 6. Running Linting and Tests

We use `tox` to run code style checks, linting, tests, and build documentation.

### Run everything
```bash
tox
```

### Run specific environments
- **Linting & Style Checks**: `tox -e lint`
- **Run Tests**: `tox -e d52`
- **Type Checking (mypy)**: `tox -e mypy`
- **Build Documentation**: `tox -e docs`

---

## 7. Running the Documentation Locally

To run this documentation server locally with live reload (so that changes are instantly previewed as you edit markdown files):

### Step 1: Install documentation dependencies
Make sure you are in your activated virtual environment and install/sync the `docs` dependency group:
```bash
uv sync --extra docs
```
*(Alternatively, you can manually install the extra dependency using `uv pip install -e .[docs]`)*

### Step 2: Start the MkDocs development server
Run the following command using the virtual environment's binary:
```bash
.venv/bin/mkdocs serve
```
Alternatively, if you have activated the virtual environment (`source .venv/bin/activate`), you can run:
```bash
mkdocs serve
```

The server will start and be available at `http://127.0.0.1:8001/`.
