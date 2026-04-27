"""Парсер и вычислитель формул"""
import re
from simpleeval import simple_eval


class FormulaEngine:
    def __init__(self, sheet):
        self.sheet = sheet

    def calc(self, expr: str):
        """Вычислить формулу"""
        try:
            processed = self._replace_refs(expr)
            return simple_eval(processed)
        except Exception:
            return "#ERROR"

    def _replace_refs(self, expr: str) -> str:
        """A1, B2 -> значения из ячеек"""
        def replace(match):
            col_str = match.group(1).upper()
            row_str = match.group(2)

            col = ord(col_str) - ord('A')
            row = int(row_str) - 1

            cell = self.sheet.get(row, col)
            val = cell.get("computed") or cell.get("value") or "0"

            try:
                return str(float(val))
            except ValueError:
                return "0"

        return re.sub(r'([A-Z]+)(\d+)', replace, expr, flags=re.IGNORECASE)
