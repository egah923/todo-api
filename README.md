# Todo List API — Docker Assignment 3

A simple Todo List REST API built with **Python, Flask, and SQLite**, packaged into a single Docker container.

This project demonstrates:

* Dockerfile fundamentals
* Docker image building
* Running a container manually
* Environment variables
* Named Docker volumes
* SQLite persistence
* Non-root containers
* Docker health checks
* Container lifecycle management

No Docker Compose is used.

## Project Structure

```text
todo-api/
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

## Build the Image

From the project directory:

```bash
docker build -t todo-api .
```

This creates an image named:

```text
todo-api:latest
```

## Create the Docker Volume

Create a named volume for persistent SQLite data:

```bash
docker volume create todos-data
```

The volume will store the SQLite database outside the container's writable filesystem.

## Run the Container

```bash
docker run -d \
  --name todo-api-python \
  --restart unless-stopped \
  -p 3000:3000 \
  -e DB_PATH=/data/todos.db \
  -v todos-data:/data \
  todo-api:latest
```

### Docker Flags Explained

| Flag                        | Description                                                  |
| --------------------------- | ------------------------------------------------------------ |
| `-d`                        | Runs the container in detached/background mode               |
| `--name todo-api-python`           | Assigns the container the name `todo-api`                    |
| `--restart unless-stopped`  | Automatically restarts the container unless manually stopped |
| `-p 3000:3000`              | Maps host port 3000 to container port 3000                   |
| `-e DB_PATH=/data/todos.db` | Sets the SQLite database path                                |
| `-v todos-data:/data`       | Mounts the named volume at `/data`                           |
| `todo-api:latest`           | Specifies the Docker image to run                            |

## Environment Variables

### DB_PATH

```text
DB_PATH=/data/todos.db
```

Defines where the SQLite database is stored inside the container.

The application defaults to:

```text
/data/todos.db
```

if the environment variable is not provided.

## API Endpoints

| Method | Endpoint     | Description   |
| ------ | ------------ | ------------- |
| GET    | `/todos`     | Get all todos |
| POST   | `/todos`     | Create a todo |
| GET    | `/todos/:id` | Get one todo  |
| PUT    | `/todos/:id` | Update a todo |
| DELETE | `/todos/:id` | Delete a todo |
| GET    | `/health`    | Health check  |

## Test the API

### Health Check

```bash
curl http://localhost:3000/health
```

### Get All Todos

```bash
curl http://localhost:3000/todos
```

### Create Todo

```bash
curl -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Docker","completed":false}'
```

### Get One Todo

```bash
curl http://localhost:3000/todos/1
```

### Update Todo

```bash
curl -X PUT http://localhost:3000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Docker and SQLite","completed":true}'
```

### Delete Todo

```bash
curl -X DELETE http://localhost:3000/todos/1
```

## Check Container Health

```bash
docker ps
```

The container should eventually show:

```text
(healthy)
```

You can also check directly:

```bash
docker inspect --format='{{.State.Health.Status}}' todo-api
```

Expected:

```text
healthy
```

## Verify Non-Root User

Check the configured user:

```bash
docker inspect --format='{{.Config.User}}' todo-api
```

Expected:

```text
appuser
```

You can also verify from inside the container:

```bash
docker exec todo-api whoami
```

Expected:

```text
appuser
```

## Test Data Persistence

Create a todo:

```bash
curl -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Test persistence","completed":false}'
```

Stop and remove the container:

```bash
docker stop todo-api
docker rm todo-api
```

Run the container again:

```bash
docker run -d \
  --name todo-api-python \
  --restart unless-stopped \
  -p 3000:3000 \
  -e DB_PATH=/data/todos.db \
  -v todos-data:/data \
  todo-api:latest
```

Check the todos:

```bash
curl http://localhost:3000/todos
```

The previously created todo should still exist.

This works because the SQLite database is stored in the named Docker volume:

```text
todos-data:/data
```

Removing the container does not remove the volume.

## Delete Persistent Data

To completely remove the stored todos:

```bash
docker stop todo-api
docker rm todo-api
docker volume rm todos-data
```

Deleting the volume removes the SQLite database and therefore the stored todos.

## Docker Architecture

```text
                    Host Machine
                         |
                         | Port 3000
                         ▼
              ┌─────────────────────┐
              │   todo-api container│
              │                     │
              │   Flask API         │
              │   Port 3000         │
              │                     │
              │   /data/todos.db    │
              └──────────┬──────────┘
                         │
                         │ mounted volume
                         ▼
                  ┌──────────────┐
                  │ todos-data   │
                  │ Named Volume │
                  └──────────────┘
```

The container can be removed and recreated without losing the database because the database is stored in the named volume rather than only inside the container.
