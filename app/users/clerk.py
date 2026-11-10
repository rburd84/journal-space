import os

import httpx
from fastapi import HTTPException

from app.users.admin import normalize_email


def get_verified_clerk_email(clerk_user_id: str) -> str:
    secret_key = os.getenv("CLERK_SECRET_KEY", "").strip()

    if not secret_key:
        raise HTTPException(
            status_code=503,
            detail="Authentication service is not configured",
        )

    try:
        response = httpx.get(
            f"https://api.clerk.com/v1/users/{clerk_user_id}",
            headers={"Authorization": f"Bearer {secret_key}"},
            timeout=5.0,
        )
        response.raise_for_status()
        user = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(
            status_code=503,
            detail="Authentication service temporarily unavailable",
        ) from error

    # Confirm the returned record matches the verified JWT identity.
    if user.get("id") != clerk_user_id:
        raise HTTPException(
            status_code=403,
            detail="Access not authorized",
        )

    primary_id = user.get("primary_email_address_id")

    for address in user.get("email_addresses", []):
        if address.get("id") != primary_id:
            continue

        if address.get("verification", {}).get("status") != "verified":
            break

        try:
            return normalize_email(address["email_address"])
        except (KeyError, ValueError):
            break

    raise HTTPException(
        status_code=403,
        detail="A verified primary email is required",
    )
