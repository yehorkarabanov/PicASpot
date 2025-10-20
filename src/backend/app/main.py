from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth.authentication import current_active_user
from app.auth.models import User
from .auth.dependencies import ActiveUserDep
from .database import create_db_and_tables, dispose_engine
from .router import router
from .settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    await create_db_and_tables()
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
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/v1")


@app.get("/")
async def root():
    return {"message": "Hello World"}