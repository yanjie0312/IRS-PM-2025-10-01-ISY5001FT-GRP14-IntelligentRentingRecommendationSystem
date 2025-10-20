from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.config import create_db_and_tables
from app.routes.property import router as property_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown

app = FastAPI(
    title="IRRS API",
    description="API for IntelligentRentingREcommendatinoSystem",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(property_router)

@app.get("/")
async def root():
    return {"message": "Welcome to IRRS"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
