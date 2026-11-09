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


def get_clerk_authorized_parties() -> list[str]:
    value = os.getenv("CLERK_AUTHORIZED_PARTIES", "")
    parties = [party.strip().rstrip("/") for party in value.split(",") if party.strip()]

    if not parties:
        raise RuntimeError("CLERK_AUTHORIZED_PARTIES is not configured")

    if any(not party.startswith(("https://", "http://localhost:", "http://127.0.0.1:")) for party in parties):
        raise RuntimeError("Invalid Clerk authorized party")

    return parties
