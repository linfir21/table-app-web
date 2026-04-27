"""Настройки приложения"""
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "data.json"

DEFAULT_ROWS = 20
DEFAULT_COLS = 5
MAX_ROWS = 100
MAX_COLS = 26  # A-Z
