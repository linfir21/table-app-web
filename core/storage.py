"""Сохранение и загрузка данных"""
import json
from pathlib import Path

from config import DATA_FILE


class Storage:
    def __init__(self, filepath=None):
        self.filepath = filepath or DATA_FILE
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def save(self, data: dict):
        """Сохранить данные в JSON"""
        serializable = {
            f"{k[0]},{k[1]}": v
            for k, v in data.items()
        }
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)

    def load(self) -> dict:
        """Загрузить данные из JSON"""
        if not self.filepath.exists():
            return {}

        with open(self.filepath, 'r', encoding='utf-8') as f:
            raw = json.load(f)

        return {
            tuple(map(int, k.split(','))): v
            for k, v in raw.items()
        }
