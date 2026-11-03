from fastapi import FastAPI

from app.core.database import Base, engine
from app.entries.router import router as entries_router
from app.journals.router import router as journals_router

app = FastAPI(title="Journal API")

# Development only. Use Alembic migrations
# instead of create_all in production.
Base.metadata.create_all(bind=engine)

app.include_router(journals_router)
app.include_router(entries_router)


@app.get("/")
def home():
    return {"Hello": "World"}


@app.get("/health")
def health():
    return {"status": "ok"}
