from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings

app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    root_path="/api",
    # lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}