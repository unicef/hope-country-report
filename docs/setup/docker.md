# Docker Setup

The application is containerized using Docker and Docker Compose.
The Docker Compose setup is split into two files:

- `compose.yml`: This file contains the base configuration for the production environment.
- `compose.override.yml`: This file contains the configuration for the development environment. It overrides the base configuration.

## Running the application

To run the application in a development environment, you can use the following command:

```bash
docker-compose up
```

This will start all the services defined in the `compose.yml` and `compose.override.yml` files.

To run the application in a production environment, you should use only the `compose.yml` file:

```bash
docker-compose -f compose.yml up
```
