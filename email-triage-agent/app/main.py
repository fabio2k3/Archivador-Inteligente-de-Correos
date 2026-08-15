from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.logging_config import setup_logging

setup_logging()

from app.api.routes import router

app = FastAPI(title="Email Triage Agent")

app.include_router(router, prefix="/api", tags=["emails"])
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return FileResponse("static/index.html")