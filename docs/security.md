# Security

The foundation phase sets the base for secure deployment:

- Environment variables are used for secrets.
- Production settings disable debug mode.
- Host names and TLS options are configured explicitly.
- The project is prepared for future checks such as `manage.py check --deploy`.
