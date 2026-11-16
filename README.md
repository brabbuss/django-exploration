# django-exploration

Learning Django and Python, coming from TypeScript and Node.

The app is a toy version of a deal closing: documents collect signatures and a
background job compiles the result.

Stack: Python 3.12, Django 6.1, Django REST Framework, Postgres 17, Celery 5 with Redis.

## What is already set up

- `config/` – the Django project. `settings.py` points at Postgres and Redis, and
  `rest_framework` and `closings` are in `INSTALLED_APPS`.
- `config/celery.py` and `config/__init__.py` – the standard Celery wiring. They are
  short and show how tasks get discovered.
- `closings/` – an empty app from `startapp`. Everything you write goes here.
- `docker-compose.yml` – Postgres on 5432 and Redis on 6379.
- The scaffold stops there. Models, views, tasks and tests are the exercise.

## Commands

```sh
docker compose up -d                      # start Postgres and Redis
docker compose stop                       # stop them when you are done

uv run python manage.py runserver         # http://127.0.0.1:8000
uv run python manage.py makemigrations    # after changing models.py
uv run python manage.py migrate
uv run python manage.py sqlmigrate closings 0001   # see the SQL a migration runs
uv run python manage.py createsuperuser   # then log in at /admin/
uv run python manage.py shell             # ORM REPL
uv run celery -A config worker -l info    # run in a second terminal
uv run pytest
```

## The work, in order

### 1. Models, migrations, admin (about 1 hour) – `closings/models.py`, `closings/admin.py`

- `Deal`: name, status, created timestamp.
- `Document`: belongs to a Deal, title, status (`draft` → `out_for_signature` →
  `signed`). Use `models.TextChoices` for the status.
- `Signer`: belongs to a Deal, name, email.
- `Signature`: joins a Document and a Signer, with a nullable `signed_at`. Add a
  unique constraint on (document, signer).
- Register all four in the admin and create a few rows by hand.

Worth noticing: what `makemigrations` generates, what `related_name` gives you, and
how a query count changes with `select_related` and `prefetch_related`.

### 2. Endpoints with one locked transition (1 to 1.5 hours) – `closings/serializers.py`, `closings/views.py`, `closings/urls.py`

- A `ModelViewSet` and serializer for Deal and Document, wired through a DRF router
  and included from `config/urls.py`.
- `POST /signatures/<id>/sign/`: inside `transaction.atomic()`, load the Document with
  `select_for_update()`, set `signed_at`, and if every signature on the document is
  now signed, move the document to `signed`.

Worth noticing: why the lock goes on the Document row and not the Signature, and
what happens to two concurrent sign requests without it.

### 3. One Celery task (about 1 hour) – `closings/tasks.py`

- `compile_closing_binder(deal_id)` as a `@shared_task`. It can write a text file
  listing the signed documents; the PDF part does not matter.
- Enqueue it when the last document on a deal becomes signed. Use
  `transaction.on_commit(...)` so the worker never runs before the row is committed.
- Make it safe to run twice, and give it `autoretry_for` with a backoff.

Worth noticing: why `on_commit` matters, and why a task takes an id and not a model
instance.

### 4. Tests (30 to 45 minutes) – `closings/tests.py`

- Signing the last signature moves the document to `signed`.
- Signing the same signature twice does not break anything.
- The task is enqueued once (`django_capture_on_commit_callbacks` or
  `CELERY_TASK_ALWAYS_EAGER` in the test).

Mark tests with `@pytest.mark.django_db`; pytest-django creates a throwaway test
database for you.
