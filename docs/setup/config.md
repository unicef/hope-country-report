# Application Configuration

The application is configured using environment variables.
The following are the main environment variables that can be used to configure the application:

- `SECRET_KEY`: A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
- `DATABASE_URL`: The URL of the database to use.
- `DATABASE_HOPE_URL`: The URL of the Hope database to use.
- `REDIS_URL`: The URL of the Redis server to use.
- `CELERY_BROKER_URL`: The URL of the Celery broker to use.
- `STREAMING_BROKER_URL`: The broker URL for the change streaming feature. Must be a RabbitMQ connection URL (e.g., `amqp://guest:guest@localhost:5672//`) or `console://` to log events locally.
- `ALLOWED_HOSTS`: A list of strings representing the host/domain names that this Django site can serve.
- `DEBUG`: A boolean that turns on/off debug mode.

For a complete list of all the available environment variables, please refer to the `settings.py` file.

---

## Configuration Validation (`smart-env`)

The project uses `smart-env` for environment variable parsing and validation. During startup and deployment (e.g. database migrations or upgrades), Django runs system checks to verify configuration.

- Required environment variables without defaults must be provided, otherwise Django will fail to start with a `SystemCheckError` showing `smart_env.E001`.
- Variables with defined default values (like `STREAMING_BROKER_URL` which defaults to `console://`) will fall back automatically unless explicitly configured.
