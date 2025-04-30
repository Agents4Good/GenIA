from typing import Annotated

from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from schema.dify import DifyState


@tool
def create_edges(
    state: Annotated[DifyState, InjectedState],
    edge_id: str,
    source_id: str,
    target_id: str
):
    """
    Cria uma aresta entre dois nós no workflow.

    Parâmetros:
        - edge_id (str): Identificador único da aresta (minúsculas, sem caracteres especiais).
        - source_id (str): ID do nó de origem da aresta (exemplo: "start_node", "llm1").
        - target_id (str): ID do nó de destino da aresta (exemplo: "answer_node", "llm2").
    """
    edge = {"id": edge_id, "source": source_id,
            "target": target_id, "type": "custom"}

    print("CREATE EDGE")
    state['edges_dicts'].append(edge)
    return edge