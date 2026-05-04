from fastapi import FastAPI

app = FastAPI(title="External Business Intel API")

@app.get("/")
def root():
    return {"status": "running", "system": "external-business-intel"}

@app.get("/health")
def health():
    return {"status": "ok"}
