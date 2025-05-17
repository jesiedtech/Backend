from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.init_db import init_db
import logging
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Jesi AI API",
    description="API for Jesi AI application",
    version=settings.VERSION
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Run database migrations on startup."""
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

@app.get("/")
async def root():
    return {"message": "Welcome to Jesi AI API"}

@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    # Check if the error is for password length
    for error in exc.errors():
        if (
            error["loc"][-1] in ("password", "new_password")
            and "Password must be at least 8 characters long" in error["msg"]
        ):
            return JSONResponse(
                status_code=422,
                content={"message": "Password must be at least 8 characters long"},
            )
    # Default behavior for other validation errors
    from fastapi.exception_handlers import request_validation_exception_handler
    return await request_validation_exception_handler(request, exc) 