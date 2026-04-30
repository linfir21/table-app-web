"""Модель таблицы с пересчётом зависимостей."""
from dataclasses import dataclass, field
import sqlite3
from typing import Optional

from core.formula import FormulaEngine
from core.deps import DependencyGraph
from core.db import Database


@dataclass
class Cell:
    value: str = ""
    formula: Optional[str] = None
    computed: Optional[str] = None
    format: str = "text"
    deps: set[str] = field(default_factory=set)


class Sheet:
    def __init__(self, db: Database):
        self._cells: dict[str, Cell] = {}
        self._deps = DependencyGraph()
        self._engine = FormulaEngine(self)
        self._db = db
        self._load()

    def get(self, addr: str) -> Optional[str]:
        addr = addr.upper()
        cell = self._cells.get(addr)
        if cell is None:
            return None
        return cell.computed if cell.computed is not None else cell.value

    def get_cell(self, addr: str) -> dict:
        addr = addr.upper()
        cell = self._cells.get(addr)
        if cell is None:
            return {"value": "", "formula": None, "computed": None, "format": "text"}
        return {
            "value": cell.value,
            "formula": cell.formula,
            "computed": cell.computed,
            "format": cell.format,
        }

    def set(self, addr: str, value: str):
        addr = addr.upper()
        cell = self._cells.setdefault(addr, Cell())

        if value.startswith("="):
            temp_deps = self._engine.get_deps(value[1:])
            if addr in temp_deps or self._deps.would_cause_cycle(addr, temp_deps):
                cell.formula = value
                cell.computed = "#CYCLE"
                cell.deps = temp_deps
                self._deps.update(addr, temp_deps)
            else:
                try:
                    result = self._engine.eval(value[1:])
                    cell.formula = value
                    cell.computed = str(result) if result is not None else "0"
                    cell.deps = temp_deps
                    self._deps.update(addr, temp_deps)
                    self._recalc_affected(addr)
                except Exception as e:
                    cell.formula = value
                    cell.computed = f"#ERROR: {e}"
                    cell.deps = set()
                    self._deps.update(addr, set())
        else:
            cell.value = value
            cell.formula = None
            cell.computed = value
            cell.deps = set()
            self._deps.update(addr, set())
            self._recalc_affected(addr)

        self._db.save(addr, cell)

    def delete(self, addr: str):
        addr = addr.upper()
        self._cells.pop(addr, None)
        self._deps.remove(addr)
        with sqlite3.connect(self._db.path) as conn:
            conn.execute("DELETE FROM cells WHERE addr = ?", (addr,))

    def clear(self):
        self._cells.clear()
        self._deps = DependencyGraph()
        self._db.clear()

    def to_dict(self) -> dict[str, dict]:
        return {
            addr: {
                "value": c.value,
                "formula": c.formula,
                "computed": c.computed,
                "format": c.format,
            }
            for addr, c in self._cells.items()
        }

    def _recalc_affected(self, start: str):
        for addr in self._deps.get_affected(start):
            cell = self._cells.get(addr)
            if cell and cell.formula:
                try:
                    result = self._engine.eval(cell.formula[1:])
                    cell.computed = str(result) if result is not None else "0"
                except Exception:
                    cell.computed = "#ERROR"
                self._db.save(addr, cell)

    def _load(self):
        data = self._db.get_all()
        for addr, c in data.items():
            self._cells[addr] = Cell(
                value=c.get("value", ""),
                formula=c.get("formula"),
                computed=c.get("computed"),
                format=c.get("format", "text"),
                deps=set(c.get("deps", [])),
            )
            if c.get("formula"):
                self._deps.update(addr, set(c.get("deps", [])))
