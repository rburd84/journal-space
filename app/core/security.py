import logging

import jwt
from fastapi import HTTPException

from app.core.config import (
    get_clerk_jwks_url,
    get_clerk_issuer,
    get_clerk_authorized_parties,
)

logger = logging.getLogger(__name__)


def get_clerk_signing_key(token: str):
    jwks_client = jwt.PyJWKClient(get_clerk_jwks_url())
    return jwks_client.get_signing_key_from_jwt(token).key


def verify_clerk_token(token: str) -> dict:
    try:
        signing_key = get_clerk_signing_key(token)

        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=get_clerk_issuer(),
            options={
                "require": ["exp", "iat", "sub", "iss"],
            },
        )

        authorized_parties = get_clerk_authorized_parties()

        if claims.get("azp") not in authorized_parties:
            raise jwt.InvalidTokenError("Unauthorized party")

        if not claims.get("sub"):
            raise jwt.InvalidTokenError("Missing subject")

        return claims

    except jwt.PyJWKClientConnectionError as error:
        logger.exception("Clerk JWKS client failed")
        raise HTTPException(
            status_code=503,
            detail="Authentication service temporarily unavailable",
        ) from error

    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        ) from error

    except (ConnectionError, TimeoutError, OSError) as error:
        logger.exception("Clerk authentication network or OS error")
        raise HTTPException(
            status_code=503,
            detail="Authentication service temporarily unavailable",
        ) from error
