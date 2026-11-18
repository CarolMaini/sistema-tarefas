# Production deployment

The production container uses Django's production settings, Gunicorn, PostgreSQL, and
WhiteNoise for static assets. The local Docker Compose workflow continues to override
the container command and settings for development.

## Required environment variables

- `DJANGO_SECRET_KEY`: unique, private Django secret.
- `DEBUG=False`: production must not enable debug mode.
- `ALLOWED_HOSTS`: comma-separated hostnames, without URL schemes.
- `CSRF_TRUSTED_ORIGINS`: comma-separated trusted origins, including `https://`.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`.

Set the platform-provided `PORT` variable when available. The container defaults to
port 8000 when it is absent. Configure persistent PostgreSQL storage and a backup
policy at the hosting provider; container-local media files are not durable storage.

## Container startup

The production command applies migrations, collects static assets, and starts Gunicorn.
Run `python src/manage.py check --deploy --settings=setup.settings.prod` with the
production environment variables before release.

## Important operational requirements

- Terminate TLS at the hosting platform and preserve the forwarded HTTPS header.
- Configure secrets in the hosting platform, never in the repository.
- Configure persistent/object storage before accepting user-uploaded media.
- Configure SMTP credentials if email verification and password reset are enabled.
- Verify database backups and restoration before treating the deployment as production-ready.
- Run smoke tests for registration, login, task workflows, authorization, and static assets.
