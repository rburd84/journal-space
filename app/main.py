import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.production import validate_production_configuration

from app.entries.router import router as entries_router
from app.journals.router import router as journals_router
from app.users.models import UserModel  # noqa: F401

validate_production_configuration()

app = FastAPI(title="Journal API")

allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
if any(
        not origin.startswith("https://")
        for origin in allowed_origins
):
    raise RuntimeError("CORS_ALLOWED_ORIGINS must contain HTTPS origins only")

if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

app.include_router(journals_router)
app.include_router(entries_router)

# Production frontend
app.include_router(journals_router, prefix="/api", include_in_schema=False)
app.include_router(entries_router, prefix="/api", include_in_schema=False)


@app.get("/")
def home():
    return {"Hello": "World"}


@app.get("/health")
def health():
    return {"status": "ok"}
