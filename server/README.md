# Orchard

Server for bunch. Written in django
This is the backend server for Bunch, a cross-platform chat application. It's built with Django and Django REST framework.

## Getting Started

1.  **Navigate to the backend directory:**

    ```bash
    cd server
    ```

2.  **Sync the project (create venv and install deps):**

    ```bash
    uv sync
    ```

3.  **Apply database migrations:**

    ```bash
    uv run --env-file .env python manage.py migrate
    ```

4.  **Run the development server (both http and ws hotreload):**

    ```bash
    uv run --env-file .env python manage.py runserver
    ```

5.  The API will be available at [http://localhost:8000](http://localhost:8000).

## Docs

The API reference docs will be available at `/api/v1/docs` in your browser after running the server.

## Key Technologies

- Django
- Django REST framework
- Daphne (for ASGI)

## API Endpoints

The API endpoints are defined in the following files:

- `server/bunch/urls.py`
- `server/core/urls.py`
- `server/users/urls.py`

For more details on the data structures, refer to the serializers:

- `server/bunch/serializers.py`
- `server/users/serializers.py`
