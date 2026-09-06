import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import ai, auth, chat, food_entries, goals, imports, reports
from app.core.config import get_settings
from app.core.errors import AppError

settings = get_settings()
logger = logging.getLogger("app")

app = FastAPI(title="Personal Calorie Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    # Anything that reaches here is a bug or a transient failure talking to Supabase/OpenAI
    # (e.g. a dropped connection on a reused pooled connection after the app sits idle).
    # Registering this via @app.exception_handler keeps it inside our CORSMiddleware layer --
    # Starlette's default fallback for uncaught exceptions runs *outside* that layer and would
    # otherwise send back a 500 with no CORS headers, which browsers report as a misleading
    # "blocked by CORS policy" error instead of the actual server error.
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again."},
    )


app.include_router(auth.router)
app.include_router(goals.router)
app.include_router(food_entries.router)
app.include_router(reports.router)
app.include_router(ai.router)
app.include_router(chat.router)
app.include_router(imports.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
