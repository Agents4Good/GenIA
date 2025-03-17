from langgraph.graph.state import CompiledStateGraph
import os
import re


def print_graph(graph: CompiledStateGraph) -> None:
    if not isinstance(graph, CompiledStateGraph):
        raise TypeError(
            "O parâmetro 'graph' deve ser uma instância de CompiledStateGraph"
        )

    graph_image = graph.get_graph().draw_mermaid_png()

    image_path = os.path.join(os.getcwd(), "graph_image.png")

    with open(image_path, "wb") as f:
        f.write(graph_image)


def extract_code(stt):
    pattern = r"```python\n?(.*?)(?:\n?```|$)"
    match = re.search(pattern, stt, re.DOTALL)

    if not match:
        lines = stt.splitlines()
        if lines:
            first_line = lines[0]
            leading_spaces = len(first_line) - len(first_line.lstrip())

            # Remove a mesma quantidade de espaços de todas as linhas
            if leading_spaces > 0:
                adjusted_lines = [
                    line[leading_spaces:]
                    if line.startswith(" " * leading_spaces)
                    else line
                    for line in lines
                ]
                return "\n".join(adjusted_lines)

        return stt
    elif match:
        code_content = match.group(1)
        return code_content
    else:
        return stt


def create_file(code: str) -> str:
    filename = "code_app.py"
    with open(filename, "w", encoding="utf-8") as arquivo:
        arquivo.write(code)
    return filename
