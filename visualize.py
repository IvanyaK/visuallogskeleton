from graphviz import Digraph
import itertools
from collections import defaultdict, deque


# ──────────────────────────────────────────────────────────────────────
#  Помощник: транзитивная редукция ориентированного графа
# ──────────────────────────────────────────────────────────────────────
def _transitive_reduction(edges):
    """
    edges – Iterable[tuple[u,v]]
    Возвращает минимальный набор рёбер, сохраняющий достижимость.
    """
    edges = set(edges)
    if not edges:
        return set()

    # adjacency list
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)

    redundant = set()                       # какие рёбра можно убрать

    for u, v in edges:
        # ищем путь u ⇒ v, минуя само ребро (u,v)
        to_visit = deque(adj[u] - {v})
        visited = {u}
        while to_visit:
            w = to_visit.popleft()
            if w == v:                      # нашли альтернативный путь
                redundant.add((u, v))
                break
            if w not in visited:
                visited.add(w)
                to_visit.extend(adj[w])

    return edges - redundant


# ──────────────────────────────────────────────────────────────────────
#  Основная функция визуализации
# ──────────────────────────────────────────────────────────────────────
def visualize_model(model, *,
                    out_file: str = "log_skeleton",
                    view: bool = True,
                    pastel_palette=None):
    """
    Рисует граф-скелет журнала процесса, применяя транзитивную
    редукцию к always_after и always_before.
    """

    # ---------- 1. подготовка эквивалентности и палитры ----------
    rep_map, fillcolor = {}, {}
    default_palette = [
        "#ffd7b5", "#c6dbef", "#c7e9c0", "#fbb4b9",
        "#d9d9d9", "#decbe4", "#b3de69", "#fccde5",
        "#bc80bd", "#8dd3c7", "#bebada", "#ffffb3",
    ]
    pastel = itertools.cycle(pastel_palette or default_palette)

    equiv_classes = model.get("equivalence", [])

    if not equiv_classes:
        equiv_classes = [{act} for act in model["activ_freq"]]
    for eq_cls in equiv_classes:
        rep = min(eq_cls)
        col = next(pastel) if len(eq_cls) > 1 else "white"
        for act in eq_cls:
            rep_map[act]   = rep
            fillcolor[act] = col

    # ---------- 2. транзитивная редукция нужных отношений ----------
    always_after   = _transitive_reduction(model.get("always_after", []))
    directly_follows = set(model.get("directly_follows", []))
    # ---------- 3. граф ----------
    dot = Digraph("LogSkeleton", format="png", engine="dot")
    dot.attr(rankdir="TB", splines="polyline", bgcolor="white")
    dot.attr("node",
             shape="Mrecord",
             style="filled",
             fontname="Times-New-Roman",
             fontsize="14")

    # ---------- 4. узлы ----------
    for act, counts in model["activ_freq"].items():
        lo, hi = min(counts), max(counts)
        interval = f"{lo}..{hi}" if lo != hi else str(hi)
        label = f"{{ {act} | {{ {rep_map[act]} | Σ={sum(counts)} | {interval} }} }}"
        dot.node(act, label=label, fillcolor=fillcolor[act])

    # ---------- 5. рёбра ----------
    for a, b in directly_follows:
        dot.edge(a, b, color="sienna", penwidth="2")

    for a, b in always_after:
        dot.edge(a, b, color="#4daf4a", style="dashed")

    # ---------- 6. вывод ----------
    dot.render(out_file, view=view, cleanup=True)
