import os

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.authentication import BaseAuthentication

DEFAULT_API_KEY = "coursework-demo-key"


def get_expected_api_key() -> str:
    return os.getenv("API_KEY", DEFAULT_API_KEY)


class ApiKeyAuthentication(BaseAuthentication):
    """Authentication class used for OpenAPI/Swagger documentation.

    Permission enforcement still happens in ApiKeyWritePermission so public read
    endpoints stay public while write endpoints require X-API-Key.
    """

    def authenticate(self, request):
        return None


class ApiKeyWritePermission(BasePermission):
    message = "Invalid or missing API key"

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True

        api_key = request.headers.get("X-API-Key")
        if api_key != get_expected_api_key():
            raise AuthenticationFailed(detail="Invalid or missing API key")
        return True
