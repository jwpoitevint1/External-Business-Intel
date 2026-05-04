from fastapi import FastAPI

from app.api.routes.trends import router as trends_router
from app.api.routes.history import router as history_router
from app.api.routes.admin import router as admin_router

app = FastAPI(title="External Business Intel API")
app.include_router(trends_router)
app.include_router(history_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {"status": "running", "system": "external-business-intel", "mode": "on-demand"}


@app.get("/health")
def health():
    return {"status": "ok"}
