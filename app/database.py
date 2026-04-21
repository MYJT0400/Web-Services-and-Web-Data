from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "books.db"
MODEL_CACHE_DIR = PROJECT_ROOT / ".models" / "fastembed-bge-small-en-v1.5"
