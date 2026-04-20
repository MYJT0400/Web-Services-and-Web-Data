"""WSGI entrypoint for traditional PythonAnywhere deployment.

The main application is FastAPI (ASGI). PythonAnywhere's classic web app
configuration expects a WSGI callable, so this file adapts the existing FastAPI
app without rewriting the project in Flask or Django.
"""

import os
import sys
from pathlib import Path

from a2wsgi import ASGIMiddleware

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# The database should be initialized once from the console before reloading the
# website. Avoid doing CSV import/embedding warmup inside every web worker import.
os.environ.setdefault("AUTO_INITIALIZE_DATABASE", "0")

from app.main import app as fastapi_app  # noqa: E402

application = ASGIMiddleware(fastapi_app)
