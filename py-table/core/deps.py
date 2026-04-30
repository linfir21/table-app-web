"""Граф зависимостей ячеек с топологической сортировкой."""
from collections import defaultdict, deque


class DependencyGraph:
    def __init__(self):
        self.depends_on: dict[str, set[str]] = {}
        self.depended_by: dict[str, set[str]] = defaultdict(set)

    def update(self, addr: str, new_deps: set[str]):
        old_deps = self.depends_on.get(addr, set())
        for dep in old_deps - new_deps:
            self.depended_by[dep].discard(addr)
        for dep in new_deps:
            self.depended_by[dep].add(addr)
        self.depends_on[addr] = new_deps

    def remove(self, addr: str):
        old_deps = self.depends_on.pop(addr, set())
        for dep in old_deps:
            self.depended_by[dep].discard(addr)

    def get_affected(self, changed: str) -> list[str]:
        # BFS: собираем все зависимые узлы
        visited = set()
        queue = deque([changed])
        nodes = []

        while queue:
            cur = queue.popleft()
            if cur in visited:
                continue
            visited.add(cur)
            nodes.append(cur)
            for dep in self.depended_by.get(cur, set()):
                if dep not in visited:
                    queue.append(dep)

        if not nodes:
            return []

        # Топологическая сортировка подграфа (Kahn)
        subgraph = set(nodes)
        in_degree = {n: 0 for n in nodes}
        for n in nodes:
            for dep in self.depends_on.get(n, set()):
                if dep in subgraph:
                    in_degree[n] += 1

        q = deque([n for n in nodes if in_degree[n] == 0])
        result = []
        while q:
            n = q.popleft()
            result.append(n)
            for dependent in self.depended_by.get(n, set()):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        q.append(dependent)

        return [r for r in result if r != changed]

    def would_cause_cycle(self, addr: str, new_deps: set[str]) -> bool:
        # DFS от new_deps: можем ли дойти до addr?
        visited = set()
        stack = list(new_deps)
        while stack:
            cur = stack.pop()
            if cur == addr:
                return True
            if cur in visited:
                continue
            visited.add(cur)
            for dep in self.depends_on.get(cur, set()):
                if dep not in visited:
                    stack.append(dep)
        return False
