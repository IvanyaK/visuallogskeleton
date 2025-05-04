from graphviz import Digraph
def visualize_model(model):
    dot = Digraph()
    for src, tgt in model["directly_follows"]:
        dot.edge(src, tgt)
    #display(dot)
    dot.render('log_skeleton_graph', view=True)
