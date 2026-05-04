from fastapi import FastAPI

from app.api.routes.trends import router as trends_router
from app.core.init_db import init_db

app = FastAPI(title="External Business Intel API")
app.include_router(trends_router)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {"status": "running", "system": "external-business-intel", "mode": "on-demand"}


@app.get("/health")
def health():
    return {"status": "ok"}
