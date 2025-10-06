# Application Configuration

The application is configured using environment variables.
The following are the main environment variables that can be used to configure the application:

- `SECRET_KEY`: A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
- `DATABASE_URL`: The URL of the database to use.
- `DATABASE_HOPE_URL`: The URL of the Hope database to use.
- `REDIS_URL`: The URL of the Redis server to use.
- `CELERY_BROKER_URL`: The URL of the Celery broker to use.
- `ALLOWED_HOSTS`: A list of strings representing the host/domain names that this Django site can serve.
- `DEBUG`: A boolean that turns on/off debug mode.

For a complete list of all the available environment variables, please refer to the `settings.py` file.
