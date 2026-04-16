import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
DEFAULT_API_KEY = "coursework-demo-key"


def get_expected_api_key() -> str:
    return os.getenv("API_KEY", DEFAULT_API_KEY)


def require_api_key(api_key: str | None = Security(API_KEY_HEADER)) -> None:
    if api_key != get_expected_api_key():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
