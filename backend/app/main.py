from fastapi import FastAPI

from .database import init_db
from .routers import router


app = FastAPI(
    title="Pothole Detection System"
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def read_root():
    return {
        "message": "Pothole Detection System is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(router)