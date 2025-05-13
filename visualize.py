from graphviz import Digraph

def visualize_model(model):
    always_after = model.get("always_after", [])
    directly_follows = model.get("directly_follows", [])

    dot = Digraph("LogSkeleton", format="png", engine="dot")
    dot.attr(rankdir="TB", splines="polyline", bgcolor="white")
    dot.attr("node",
             shape="Mrecord",
             style="filled",
             fontname="Times-New-Roman",
             fontsize="14")

    for act, counts in model["activ_freq"].items():
        lo, hi = min(counts), max(counts)
        interval = f"{lo}..{hi}" if lo != hi else str(hi)
        label = f"{{ {act} | {{ Name | {sum(counts)} | {interval} }} }}"
        dot.node(act, label=label, fillcolor='antiquewhite')

    for a, b in directly_follows:
        dot.edge(a, b, color="sienna", penwidth="2")

    for a, b in always_after:
        dot.edge(a, b, color="#4daf4a", style="dashed")

    dot.render('log_skeleton_graph', view=True, cleanup=True)
