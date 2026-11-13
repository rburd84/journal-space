"""Regression checks for PostgreSQL driver selection."""

import pytest
from sqlalchemy.engine import make_url

from app.core.database_url import normalize_database_url


@pytest.mark.parametrize("prefix", [
    "postgres://",
    "postgresql://",
    "postgresql+psycopg2://",
    "postgresql+psycopg://",
])
def test_postgresql_uses_psycopg3(prefix):
    result = make_url(normalize_database_url(
        f"{prefix}testuser:secret@localhost:5432/stillspace"
    ))
    assert result.drivername == "postgresql+psycopg"
    assert result.database == "stillspace"


def test_sqlite_is_unchanged():
    url = "sqlite:///./journal.db"
    assert normalize_database_url(url) == url


def test_special_characters_and_options_survive():
    original = (
        "postgresql://testuser:p%40ss%25word@localhost/stillspace"
        "?sslmode=require"
    )
    result = make_url(normalize_database_url(original))
    assert result.drivername == "postgresql+psycopg"
    assert result.password == "p@ss%word"
    assert result.query["sslmode"] == "require"


def test_already_normalized_url_is_stable():
    original = "postgresql+psycopg://testuser:secret@localhost/stillspace"
    assert normalize_database_url(normalize_database_url(original)) == original
