from typing import Annotated

from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command


@tool
def create_edges(
    tool_call_id: Annotated[str, InjectedToolCallId],
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
    return Command(
        update={
            "edges_dicts": [edge],
            "messages": [
                ToolMessage(
                    f"Successfully added the edge between {source_id} and {target_id}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )
