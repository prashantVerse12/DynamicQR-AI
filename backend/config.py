import os


DEVELOPMENT_JWT_SECRET = "dynamic_qr_ai_development_secret"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./qr_codes.db")
JWT_SECRET = os.getenv("JWT_SECRET", DEVELOPMENT_JWT_SECRET)

if ENVIRONMENT == "production" and (
    not JWT_SECRET or JWT_SECRET == DEVELOPMENT_JWT_SECRET
):
    raise RuntimeError(
        "JWT_SECRET must be set to a non-development value when ENVIRONMENT=production."
    )

AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://127.0.0.1:9000").rstrip("/")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")


def _parse_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


CORS_ORIGINS = _parse_origins(
    os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
)
