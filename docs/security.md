# Security

This document describes security controls present in the current implementation and operational safeguards still required before a public production launch.

## Application controls

- Production settings require a secret key, explicit allowed hosts and trusted CSRF origins.
- Production configuration disables debug mode and enables HTTPS-related protections, secure cookies, HSTS and clickjacking protection.
- Authentication and workspace authorization are checked server-side. Access to workspace data is scoped to the user's active membership and role.
- Inactive accounts are excluded from workspace access and task assignment.
- Task execution and assignment workflows validate ownership, state and workspace access before changing records.
- Uploads are restricted by allowed file types and a 10 MB size limit; stored names are randomized.
- Attachment downloads require authentication and authorization to the related workspace.
- Important workflow changes create audit events; related multi-step writes use database transactions.
- The production container runs as an unprivileged user.

## CI security and quality checks

The GitHub Actions workflow runs Django's production deployment checks using CI-only credentials, verifies migration consistency, runs tests, builds the production image and performs a container smoke test. These checks improve confidence but do not replace a security review or production monitoring.

Dependabot is configured to check Python packages, GitHub Actions and Docker images weekly.

## Before production launch

- Store secrets only in the hosting provider's secret manager or environment configuration.
- Terminate TLS correctly and preserve the forwarded HTTPS header.
- Configure durable media/object storage and verify file permissions.
- Configure SMTP credentials if email verification or password reset is enabled.
- Configure PostgreSQL backups and test restoration.
- Review logs and monitoring for sensitive data exposure.
- Configure repository rules requiring pull requests and successful CI checks on `main`.

The CI smoke test is not a production deployment, and the repository is not considered production-ready until the operational items above are completed and verified.
