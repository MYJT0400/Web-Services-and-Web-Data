import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

# Read API key from HTTP header: X-API-Key
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
DEFAULT_API_KEY = "coursework-demo-key"


def get_expected_api_key() -> str:
    # Allows overriding the default key via environment variable.
    return os.getenv("API_KEY", DEFAULT_API_KEY)


def require_api_key(api_key: str | None = Security(API_KEY_HEADER)) -> None:
    # Dependency used on write endpoints (POST/PUT/DELETE).
    if api_key != get_expected_api_key():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
