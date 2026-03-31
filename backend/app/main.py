from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .routers import signals

# Create tables if they don't exist (SQLite)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Trading Signal Tracker")

# Allow the Next.js dev server (default http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signals.router)


@app.get("/")
def root():
    return {"message": "Signal Tracker API – see /docs for Swagger UI"}