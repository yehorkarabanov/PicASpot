from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables, dispose_engine
from app.router import router
from app.settings import settings
from app.core.utils import generate_users

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # # Startup: Create tables
    # await create_db_and_tables()
    #
    # # Startup: Create default users
    # await generate_users()

    yield
    # Shutdown: Dispose engine
    await dispose_engine()


app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    root_path="/api",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(router, prefix="/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the picASpot API!"}
