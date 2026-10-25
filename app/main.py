
from fastapi import FastAPI

app = FastAPI(
    title="PRISM API",
    description="Developer intelligence and repository analytics",
    version="0.1.0"
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "prism-api"
    }
