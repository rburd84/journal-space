import pytest

from app.core.production import validate_production_configuration


@pytest.fixture(autouse=True)
def clear_settings(monkeypatch):
    for key in (
        "STILLSPACE_ENV", "DATABASE_URL", "CLERK_ISSUER",
        "CLERK_AUTHORIZED_PARTIES", "CORS_ALLOWED_ORIGINS",
    ):
        monkeypatch.delenv(key, raising=False)


def configure_valid(monkeypatch):
    monkeypatch.setenv("STILLSPACE_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost/stillspace")
    monkeypatch.setenv("CLERK_ISSUER", "https://clerk.example.com")
    monkeypatch.setenv("CLERK_AUTHORIZED_PARTIES", "https://stillspace.example.com")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://stillspace.example.com")


def test_development_requires_no_production_settings():
    validate_production_configuration()


def test_valid_production_settings(monkeypatch):
    configure_valid(monkeypatch)
    validate_production_configuration()


@pytest.mark.parametrize("key,value", [
    ("DATABASE_URL", "sqlite:///./journal.db"),
    ("DATABASE_URL", ""),
    ("CLERK_ISSUER", "http://clerk.example.com"),
    ("CLERK_ISSUER", ""),
    ("CLERK_AUTHORIZED_PARTIES", "http://localhost:5173"),
    ("CLERK_AUTHORIZED_PARTIES", ""),
    ("CORS_ALLOWED_ORIGINS", "*"),
    ("CORS_ALLOWED_ORIGINS", ""),
    ("CORS_ALLOWED_ORIGINS", "https://evil.example.com"),
    ("CORS_ALLOWED_ORIGINS", "https://stillspace.example.com/path"),
])
def test_rejects_unsafe_production_settings(monkeypatch, key, value):
    configure_valid(monkeypatch)
    monkeypatch.setenv(key, value)
    with pytest.raises(RuntimeError):
        validate_production_configuration()
