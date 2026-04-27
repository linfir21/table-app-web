"""Модель данных таблицы"""
from core.formula import FormulaEngine
from core.storage import Storage


class Sheet:
    def __init__(self, storage=None):
        self._data = {}
        self._storage = storage or Storage()
        self._formula = FormulaEngine(self)
        self._load()

    def get(self, row: int, col: int) -> dict:
        """Получить ячейку"""
        return self._data.get((row, col), {"value": "",
                                           "formula": None, "computed": None})

    def set(self, row: int, col: int, value: str):
        cell = self._data.setdefault((row, col), {})

        if value.startswith("="):
            cell["formula"] = value
            cell["computed"] = self._formula.calc(value[1:])
        else:
            cell["value"] = value
            cell["formula"] = None
            cell["computed"] = value

        self._save()

    def delete(self, row: int, col: int):
        """Удалить ячейку"""
        self._data.pop((row, col), None)
        self._save()

    def clear(self):
        """Очистить всё"""
        self._data.clear()
        self._save()

    def _save(self):
        """Сохранить в файл"""
        self._storage.save(self._data)

    def _load(self):
        """Загрузить из файла"""
        self._data = self._storage.load()
