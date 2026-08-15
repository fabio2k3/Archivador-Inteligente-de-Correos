from fastapi import FastAPI
from app.core.logging_config import setup_logging

setup_logging()

from app.api.routes import router

app = FastAPI(title="Email Triage Agent")

app.include_router(router, prefix="/api", tags=["emails"])


@app.get("/")
def read_root():
    return {"status": "ok", "service": "email-triage-agent"}