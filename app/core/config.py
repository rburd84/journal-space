import os


def get_clerk_issuer() -> str:
    issuer = os.getenv("CLERK_ISSUER", "").strip().rstrip("/")

    if not issuer:
        raise RuntimeError("CLERK_ISSUER is not configured")

    if not issuer.startswith("https://"):
        raise RuntimeError("CLERK_ISSUER must use HTTPS")

    return issuer


def get_clerk_jwks_url() -> str:
    return f"{get_clerk_issuer()}/.well-known/jwks.json"
