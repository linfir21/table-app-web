"""Движок формул на Lark — парсинг + вычисление + извлечение зависимостей."""
import re
from lark import Lark, Transformer

_grammar = r"""
?start: expr

?expr: term
     | expr "+" term   -> add
     | expr "-" term   -> sub

?term: factor
     | term "*" factor -> mul
     | term "/" factor -> div

?factor: NUMBER       -> number
       | cell_ref
       | func_call
       | "(" expr ")"

func_call: NAME "(" [arg_list] ")"

arg_list: arg ("," arg)*

arg: CELL_REF ":" CELL_REF -> range
   | expr

cell_ref: CELL_REF

CELL_REF: /[A-Z]+[0-9]+/
NAME: /[A-Z][A-Z_]+/
NUMBER: /-?\d+(\.\d+)?/

%import common.WS
%ignore WS
"""

_parser = Lark(_grammar, parser="lalr", maybe_placeholders=False)


def _col_to_num(col: str) -> int:
    num = 0
    for ch in col.upper():
        num = num * 26 + (ord(ch) - ord("A") + 1)
    return num


def _num_to_col(num: int) -> str:
    col = ""
    while num > 0:
        num, rem = divmod(num - 1, 26)
        col = chr(ord("A") + rem) + col
    return col


def expand_range(start: str, end: str) -> list[str]:
    def parse(addr):
        m = re.match(r"([A-Z]+)(\d+)", addr.upper())
        return m.group(1), int(m.group(2))

    sc, sr = parse(start)
    ec, er = parse(end)
    sc_n, ec_n = _col_to_num(sc), _col_to_num(ec)

    cells = []
    for c in range(min(sc_n, ec_n), max(sc_n, ec_n) + 1):
        for r in range(min(sr, er), max(sr, er) + 1):
            cells.append(f"{_num_to_col(c)}{r}")
    return cells


def _flatten(args):
    out = []
    for a in args:
        if isinstance(a, list):
            out.extend(a)
        else:
            out.append(a)
    return out


def _apply_func(name: str, raw_args):
    vals = _flatten(raw_args)
    nums = [v for v in vals if isinstance(v, (int, float))]
    if name == "SUM":
        return sum(nums)
    elif name == "AVERAGE":
        return sum(nums) / len(nums) if nums else 0
    elif name == "MIN":
        return min(nums) if nums else 0
    elif name == "MAX":
        return max(nums) if nums else 0
    elif name == "COUNT":
        return len(nums)
    return f"#FUNC?{name}"


class _EvalTransformer(Transformer):
    def __init__(self, sheet_getter):
        self._get = sheet_getter
        self.deps: set[str] = set()

    def number(self, args):
        return float(args[0])

    def cell_ref(self, args):
        addr = str(args[0]).upper()
        self.deps.add(addr)
        val = self._get(addr)
        try:
            return float(val) if val is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def range(self, args):
        start, end = str(args[0]).upper(), str(args[1]).upper()
        cells = expand_range(start, end)
        self.deps.update(cells)
        return [self._to_float(c) for c in cells]

    def _to_float(self, addr: str):
        val = self._get(addr)
        try:
            return float(val) if val is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def func_call(self, args):
        name = str(args[0]).upper()
        params = args[1] if len(args) > 1 else []
        if params is None:
            params = []
        return _apply_func(name, params)

    def arg_list(self, args):
        return list(args)

    def add(self, a):
        return a[0] + a[1]

    def sub(self, a):
        return a[0] - a[1]

    def mul(self, a):
        return a[0] * a[1]

    def div(self, a):
        return a[0] / a[1] if a[1] != 0 else float("inf")


class FormulaEngine:
    def __init__(self, sheet):
        self.sheet = sheet

    def eval(self, expr: str):
        tree = _parser.parse(expr)
        tr = _EvalTransformer(self.sheet.get)
        return tr.transform(tree)

    def get_deps(self, expr: str) -> set[str]:
        tree = _parser.parse(expr)
        tr = _EvalTransformer(self.sheet.get)
        tr.transform(tree)
        return tr.deps
