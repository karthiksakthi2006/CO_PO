# Security Policy — CO-ATTAIN PRO AI

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Yes    |

## Authentication & Password Security

- All passwords are hashed using **Argon2id** (memory-hard, side-channel resistant) via `passlib[argon2]`.
- Minimum password entropy: 8 characters, mixed case, digit, special character enforced at schema validation layer.
- Plaintext passwords are **never** stored or logged.

## JWT Token Security

- Tokens include `sub` (user ID), `role`, `iat` (issued-at), `exp` (expiry) claims.
- Default token expiry: **60 minutes** (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`).
- Token blacklist table (`token_blacklist`) invalidates tokens on user logout.
- Secret key must be ≥ 32 random bytes — generated at first boot if not supplied.

## Role-Based Access Control (RBAC)

| Endpoint Category | STUDENT | FACULTY | HOD | SUPER_ADMIN |
|---|---|---|---|---|
| Read own performance | ✅ | ✅ | ✅ | ✅ |
| Read courses/COs | ✅ | ✅ | ✅ | ✅ |
| Create/edit courses | ❌ 403 | ✅ | ✅ | ✅ |
| Import marks | ❌ 403 | ✅ | ✅ | ✅ |
| Run attainment | ❌ 403 | ✅ | ✅ | ✅ |
| Create interventions | ❌ 403 | ✅ | ✅ | ✅ |
| View audit logs | ❌ 403 | ❌ 403 | ✅ | ✅ |
| Manage users | ❌ 403 | ❌ 403 | ❌ 403 | ✅ |

Role enforcement is implemented as a FastAPI dependency (`require_roles()`) injected at every router function — not just middleware — ensuring granular, per-endpoint control.

## Environment Variables

Never commit secrets. Copy `.env.example` to `.env` and fill in your own values:

```
SECRET_KEY=<minimum 32 random bytes, e.g. from: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=sqlite:///./co_attain.db
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

The `.env` file is listed in `.gitignore` and will **never** be pushed to version control.

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not open a public GitHub issue**.

Contact the maintainer directly at:
- **GitHub**: [@Kathirvel005](https://github.com/Kathirvel005)

Include:
1. Description of the vulnerability.
2. Steps to reproduce.
3. Potential impact.
4. Suggested fix (optional).

You will receive a response within 48 hours. Confirmed vulnerabilities will be patched in a private branch and disclosed responsibly after a fix is released.
