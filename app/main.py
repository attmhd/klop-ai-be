import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import Routers
try:
    from app.modules.generation.router import router as gen_router
except ModuleNotFoundError:
    # Fallback when running without package context (e.g., python app/main.py)
    from .modules.generation.router import router as gen_router

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Klop! AI Assessment API",
    description="AI untuk generate soal, scoring, dan insight.",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",
)

# --- 1. CONFIGURATION: CORS (Wajib untuk Frontend) ---
origins = [
    "http://localhost:3000",  # React default port
    "http://localhost:8000",  # Local API
    "*",  # Allow All (Gunakan spesifik domain saat production!)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)


# --- 2. GLOBAL EXCEPTION HANDLER (Envelope Pattern) ---
# Menangani Error tak terduga (500 Internal Server Error)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "success": False,
            "message": f"Internal Server Error: {str(exc)}",
            "data": None,
        },
    )


# Menangani HTTP Exception (misal: 404 Not Found, 400 Bad Request)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "success": False,
            "message": exc.detail,
            "data": None,
        },
    )


# --- 3. REGISTER ROUTERS ---
app.include_router(gen_router, prefix="/api/v1/generate", tags=["Generation"])


# --- 4. HEALTH CHECK ---
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "Klop! AI", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to Klop! AI API. Go to /docs for Swagger UI."}
