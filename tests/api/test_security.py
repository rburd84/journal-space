from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from app.core.security import verify_clerk_token


def test_valid_rs256_token_is_accepted():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "user_test123",
            "iss": "https://example.com",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        private_key,
        algorithm="RS256",
    )

    with (
        patch(
            "app.core.security.get_clerk_signing_key",
            return_value=private_key.public_key(),
        ),
        patch(
            "app.core.security.get_clerk_issuer",
            return_value="https://example.com",
        ),
    ):
        claims = verify_clerk_token(token)

        assert claims["sub"] == "user_test123"
        assert claims["iss"] == "https://example.com"


def test_expired_rs256_token_is_rejected():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "user_test123",
            "iss": "https://example.com",
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
        },
        private_key,
        algorithm="RS256",
    )

    with (
        patch(
            "app.core.security.get_clerk_signing_key",
            return_value=private_key.public_key(),
        ),
        patch(
            "app.core.security.get_clerk_issuer",
            return_value="https://example.com",
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication token"


def test_wrong_issuer_is_rejected():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "user_test123",
            "iss": "https://wrong-issuer.example.com",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        private_key,
        algorithm="RS256",
    )

    with (
        patch(
            "app.core.security.get_clerk_signing_key",
            return_value=private_key.public_key(),
        ),
        patch(
            "app.core.security.get_clerk_issuer",
            return_value="https://example.com",
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication token"


def test_invalid_signature_is_rejected():
    trusted_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    untrusted_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "user_test123",
            "iss": "https://example.com",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        untrusted_key,
        algorithm="RS256",
    )

    with (
        patch(
            "app.core.security.get_clerk_signing_key",
            return_value=trusted_key.public_key(),
        ),
        patch(
            "app.core.security.get_clerk_issuer",
            return_value="https://example.com",
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication token"


@pytest.mark.parametrize("missing_claim", ["exp", "iat", "sub", "iss"])
def test_missing_required_claim_is_rejected(missing_claim):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    now = datetime.now(timezone.utc)

    claims = {
        "sub": "user_test123",
        "iss": "https://example.com",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    del claims[missing_claim]

    token = jwt.encode(claims, private_key, algorithm="RS256")

    with (
        patch(
            "app.core.security.get_clerk_signing_key",
            return_value=private_key.public_key(),
        ),
        patch(
            "app.core.security.get_clerk_issuer",
            return_value="https://example.com",
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(token)

    assert exc_info.value.status_code == 401


def test_empty_subject_is_rejected():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "",
            "iss": "https://example.com",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        private_key,
        algorithm="RS256",
    )

    with (
        patch(
            "app.core.security.get_clerk_signing_key",
            return_value=private_key.public_key(),
        ),
        patch(
            "app.core.security.get_clerk_issuer",
            return_value="https://example.com",
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(token)

    assert exc_info.value.status_code == 401


def test_future_not_before_is_rejected():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "user_test123",
            "iss": "https://example.com",
            "iat": now,
            "nbf": now + timedelta(minutes=10),
            "exp": now + timedelta(minutes=15),
        },
        private_key,
        algorithm="RS256",
    )

    with (
        patch(
            "app.core.security.get_clerk_signing_key",
            return_value=private_key.public_key(),
        ),
        patch(
            "app.core.security.get_clerk_issuer",
            return_value="https://example.com",
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(token)

    assert exc_info.value.status_code == 401


def test_hs256_algorithm_is_rejected():
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "user_test123",
            "iss": "https://example.com",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        "local-test-secret-at-least-32-bytes-long",
        algorithm="HS256",
    )

    with (
        patch(
            "app.core.security.get_clerk_signing_key",
            return_value="local-test-secret-at-least-32-bytes-long",
        ),
        patch(
            "app.core.security.get_clerk_issuer",
            return_value="https://example.com",
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(token)

    assert exc_info.value.status_code == 401


@pytest.mark.parametrize(
    "failure,expected_status",
    [
        (jwt.PyJWKClientConnectionError("JWKS unavailable"), 503),
        (ConnectionError("Connection failed"), 503),
        (TimeoutError("Connection timed out"), 503),
        (jwt.PyJWKClientError("Signing key not found"), 401),
    ],
)
def test_signing_key_lookup_failures(failure, expected_status):
    with patch(
            "app.core.security.get_clerk_signing_key",
            side_effect=failure,
    ):
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token("test-token")

    assert exc_info.value.status_code == expected_status

    if expected_status == 503:
        assert (
                exc_info.value.detail
                == "Authentication service temporarily unavailable"
        )
    else:
        assert exc_info.value.detail == "Invalid authentication token"
