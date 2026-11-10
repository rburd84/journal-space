from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.dependencies import get_clerk_user_id


def test_missing_credentials_are_rejected():
    with pytest.raises(HTTPException) as exc_info:
        get_clerk_user_id(None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication required"


def test_valid_credentials_return_verified_user_id():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="test-token",
    )

    with patch(
            "app.core.dependencies.verify_clerk_token",
            return_value={"sub": "user_test123"},
    ) as mock_verify:
        user_id = get_clerk_user_id(credentials)

    assert user_id == "user_test123"
    mock_verify.assert_called_once_with("test-token")
