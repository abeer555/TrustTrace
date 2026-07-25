from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import ingest, alerts, entities, dashboard
from app.core.database import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="TrustTrace API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api/v1", tags=["Ingest"])
app.include_router(alerts.router, prefix="/api/v1", tags=["Alerts"])
app.include_router(entities.router, prefix="/api/v1", tags=["Entities"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "Welcome to TrustTrace API"}
