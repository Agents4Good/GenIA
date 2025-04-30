from typing import Annotated

from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.prebuilt import InjectedState
from schema.dify import DifyState


@tool
def create_http_node(
    state: Annotated[DifyState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    title: str,
    node_id: str
):
    """
    Cria um nó HTTP que possibilita requisições .

    Parametros:
        - title (str): Nome do nó.
        - node_id (str): Identificador único baseado no nome (minúsculas, sem caracteres especiais).
    """

    http_node = {
        "id": node_id,
        "type": "custom",
        "data": {
            "body": {
                "type": None,
                "data": []
            },
            "title": title,
            "type": "http-request"
        }
    }
    state["nodes_dicts"].append(http_node)

    print("HTTP NODE")
    return http_node
