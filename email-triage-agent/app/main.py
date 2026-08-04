from fastapi import FastAPI

app = FastAPI(title="Email Triage Agent")

@app.get("/")
def read_root():
    return {"status": "ok", "service": "email-triage-agent"}