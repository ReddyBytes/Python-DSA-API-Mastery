# 🔒 Security — Theory
> Protect systems from unauthorised access, abuse, and attacks — from API keys to DDoS mitigation at scale.

---

## 📋 Contents

```
1.  Authentication vs authorization — who you are vs what you can do
2.  OAuth2 flow — authorization code, client credentials, implicit
3.  JWT — structure, signing, validation, and pitfalls
4.  API keys — issuance, rotation, and scoping
5.  Rate limiting algorithms — token bucket, leaky bucket, sliding window
6.  HTTPS / TLS — handshake, certificates, and forward secrecy
7.  DDoS protection — volumetric, protocol, and application layer attacks
8.  OWASP Top 10 — injection, broken auth, XSS, and more
```

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
authentication (OAuth2/JWT/API keys) · authorization checks · rate limiting · secrets management

**Should Learn** — Important for real projects, comes up regularly:
HTTPS/TLS · DDoS mitigation strategies · OWASP Top 10 categories · audit logging

**Good to Know** — Useful in specific situations, not always tested:
zero-trust architecture principles · JWT limitations (revocation complexity)

**Reference** — Know it exists, look up syntax when needed:
WAF configuration · mTLS · FIDO2/WebAuthn · SSO/SAML

---

## 📖 **Main content**: [security_fundamentals.md](./security_fundamentals.md)

---

## 🔑 Secrets Management — Never Hardcode Credentials

> A hardcoded database password in source code is like writing your house key on the front door. Secrets management externalizes credentials so they never touch version control and can be rotated without redeploying code.

**Secrets** include: database passwords, API keys, JWT signing keys, TLS private keys, OAuth client secrets, encryption keys.

**The wrong ways (never do these):**

```python
# WRONG: hardcoded in source code
DATABASE_URL = "postgresql://admin:s3cr3t@db.prod.example.com/mydb"

# WRONG: in .env file checked into git
# .env: SECRET_KEY=my-secret-key
```

**The right pattern — environment-based injection:**

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str           # ← injected at runtime, never in code
    jwt_secret: str
    stripe_api_key: str

    class Config:
        env_file = ".env"       # ← .env in .gitignore for local dev only

settings = Settings()           # ← reads from environment or .env file
```

**AWS Secrets Manager pattern (production standard):**

```python
import boto3
import json

def get_secret(secret_name: str) -> dict:
    """Fetch secret from AWS Secrets Manager at startup."""
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

# At application startup — fetch once, cache in memory:
db_creds = get_secret("prod/myapp/database")
DATABASE_URL = f"postgresql://{db_creds['username']}:{db_creds['password']}@..."
```

**HashiCorp Vault pattern (multi-cloud / on-premise):**

```python
import hvac

client = hvac.Client(url="https://vault.internal:8200", token=os.environ["VAULT_TOKEN"])

secret = client.secrets.kv.v2.read_secret_version(path="myapp/database")
db_password = secret["data"]["data"]["password"]
```

**Secrets rotation without downtime:**

```
1. Generate new secret version in Vault/Secrets Manager
2. Update all replicas to accept BOTH old and new secret (dual-accept period)
3. Rotate: switch to new secret in application
4. Revoke old secret after all instances confirmed migrated

Key: Never have a moment where no valid secret exists.
```

**Principles:**
- **Least privilege** — each service gets only the secrets it needs
- **Short TTL** — prefer short-lived credentials (AWS IAM roles) over long-lived passwords
- **Audit trail** — every secret access should be logged
- **Rotation** — rotate secrets on schedule, not just on breach
- **No secrets in logs** — mask credentials in structured logs

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ⬅️ Previous | [12 — Microservices](../12_microservices/theory.md) |
| ➡️ Next | [14 — Observability](../14_observability/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Microservices — Interview Q&A](../12_microservices/interview.md) &nbsp;|&nbsp; **Next:** [Security Fundamentals →](./security_fundamentals.md)

**Related Topics:** [Security Fundamentals](./security_fundamentals.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
