"""SQLite-хранилище для ячеек."""
import json
import sqlite3


class Database:
    def __init__(self, path: str = "data/sheet.db"):
        self.path = path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cells (
                    addr TEXT PRIMARY KEY,
                    value TEXT,
                    formula TEXT,
                    computed TEXT,
                    format TEXT DEFAULT 'text',
                    deps TEXT
                )
                """
            )

    def get_all(self) -> dict[str, dict]:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM cells").fetchall()
            return {
                row["addr"]: {
                    "value": row["value"] or "",
                    "formula": row["formula"],
                    "computed": row["computed"],
                    "format": row["format"] or "text",
                    "deps": json.loads(row["deps"]) if row["deps"] else [],
                }
                for row in rows
            }

    def save(self, addr: str, cell):
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT INTO cells (addr, value, formula, computed, format, deps)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(addr) DO UPDATE SET
                    value=excluded.value,
                    formula=excluded.formula,
                    computed=excluded.computed,
                    format=excluded.format,
                    deps=excluded.deps
                """,
                (
                    addr,
                    cell.value,
                    cell.formula,
                    cell.computed,
                    cell.format,
                    json.dumps(list(cell.deps)),
                ),
            )

    def clear(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("DELETE FROM cells")
