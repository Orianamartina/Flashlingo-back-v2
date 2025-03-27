# Flashlingo Project

## Overview

Flashlingo is a flashcard-based game to help users learn languages. The project uses the following technologies:
- **Django** for the backend
- **Daphne** for WebSocket support
- **MongoDB and sqlite** as the databases
- **Docker** for containerization

## Requirements

To run the application, you need the following installed:

- [Docker](https://www.docker.com/get-started) (for running containers)
- [Docker Compose](https://docs.docker.com/compose/install/) (for managing multi-container applications)

- Create a db.sqlite3 file on the root folder

## Setup Instructions

### 1. Clone the repository

### 2. Create a .env file in the root directory and configure the necessary environment variables.
``` 
DEBUG=
SECRET_KEY=
DJANGO_SETTINGS_MODULE=
MONGO_URL=
```

### 3. Build and start the services using Docker Compose:
```
make setup
```

### 4. Run the application
```
make run
```

### 5. Shutdown the services:
```
make down
```