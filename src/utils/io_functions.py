from langgraph.graph.state import CompiledStateGraph
import os

def print_graph(graph: CompiledStateGraph) -> None:

    if not isinstance(graph, CompiledStateGraph):
        raise TypeError("O parâmetro 'graph' deve ser uma instância de CompiledStateGraph")

    graph_image = graph.get_graph().draw_mermaid_png()

    image_path = os.path.join(os.getcwd(), "graph_image.png")

    with open(image_path, "wb") as f:
        f.write(graph_image)
