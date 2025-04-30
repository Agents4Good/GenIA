from typing import Annotated, Literal

from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from .utils import create_logic_node
from langgraph.prebuilt import InjectedState
from schema.dify import DifyState


@tool
def create_logic_edges(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[DifyState, InjectedState],
    edge_id: str,
    source_id: str,
    source_handle: Literal["true", "false"],
    target_id: str
):
    """
    Cria uma aresta entre um nó de lógica e outro nó qualquer do workflow.
    Há duas saídas do mesmo nó de lógica, uma para "true" e outra para "false".

    Parâmetros:
        - edge_id (str): Identificador único da aresta (minúsculas, sem caracteres especiais).
        - source_id (str): ID do nó de lógica (exemplo: "start_with_node").
        - source_handle (Literal["true", "false"]): Para qual saída booleana a aresta deve ser criada.
        - target_id (str): ID do nó de destino da aresta (exemplo: "llm1", "llm2").
    """
    logic_edge = {"id": edge_id, "source": source_id,
                  "sourceHandle": source_handle, "target": target_id, "type": "custom"}

    state["nodes_dicts"].append(logic_edge)

    print("CREATE LOGIC EDGE")
    return logic_edge


@tool
def create_start_with_logic_node(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[DifyState, InjectedState],
    title: str,
    node_id: str,
    value: str,
    context_variable: str
):
    """
    Cria um nó de lógica que verifica se uma variável começa com um valor específico.

    Parâmetros:
        - title (str): Nome do nó.
        - node_id (str): Identificador único baseado no nome (minúsculas, sem caracteres especiais).
        - value (str): Valor a ser verificado se é o início da variável.
        - context_variable (str): Variável de contexto compartilhada entre nós (exemplo: use "sys.query" para receber o contexto do nó inicial, "<previous_node_id>.text" para receber o contexto de outros nós).
    """
    start_with_node = create_logic_node(
        title=title,
        node_id=node_id,
        value=value,
        comparison_operator="start with",
        context_variable=context_variable
    )

    state["nodes_dicts"].append(start_with_node)

    print("START WITH NODE")
    return start_with_node


@tool
def create_end_with_logic_node(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[DifyState, InjectedState],
    title: str,
    node_id: str,
    value: str,
    context_variable: str
):
    """
    Cria um nó de lógica que verifica se uma variável termina com um valor específico.

    Parâmetros:
        - title (str): Nome do nó.
        - node_id (str): Identificador único baseado no nome (minúsculas, sem caracteres especiais).
        - value (str): Valor a ser verificado se é o final da variável.
        - context_variable (str): Variável de contexto compartilhada entre nós (exemplo: use "sys.query" para receber o contexto do nó inicial, "<previous_node_id>.text" para receber o contexto de outros nós).
    """
    end_with_node = create_logic_node(
        title=title,
        node_id=node_id,
        value=value,
        comparison_operator="end with",
        context_variable=context_variable
    )

    state["nodes_dicts"].append(end_with_node)

    print("END WITH NODE")
    return end_with_node


@tool
def create_contains_logic_node(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[DifyState, InjectedState],
    title: str,
    node_id: str,
    value: str,
    context_variable: str
):
    """
    Cria um nó de lógica que verifica se uma variável contém um valor específico.

    Parâmetros:
        - title (str): Nome do nó.
        - node_id (str): Identificador único baseado no nome (minúsculas, sem caracteres especiais).
        - value (str): Valor a ser verificado se está contido na variável.
        - context_variable (str): Variável de contexto compartilhada entre nós (exemplo: use "sys.query" para receber o contexto do nó inicial, "<previous_node_id>.text" para receber o contexto de outros nós).
    """
    contains_node = create_logic_node(
        title=title,
        node_id=node_id,
        value=value,
        comparison_operator="contains",
        context_variable=context_variable
    )

    state["nodes_dicts"].append(contains_node)

    print("CONTAINS NODE")
    return contains_node


@tool
def create_not_contains_logic_node(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[DifyState, InjectedState],
    title: str,
    node_id: str,
    value: str,
    context_variable: str
):
    """
    Cria um nó de lógica que verifica se uma variável não contém um valor específico.

    Parâmetros:
        - title (str): Nome do nó.
        - node_id (str): Identificador único baseado no nome (minúsculas, sem caracteres especiais).
        - value (str): Valor a ser verificado se não está contido na variável.
        - context_variable (str): Variável de contexto compartilhada entre nós (exemplo: use "sys.query" para receber o contexto do nó inicial, "<previous_node_id>.text" para receber o contexto de outros nós).
    """
    not_contains_node = create_logic_node(
        title=title,
        node_id=node_id,
        value=value,
        comparison_operator="not contains",
        context_variable=context_variable
    )

    state["nodes_dicts"].append(not_contains_node)

    print("NOT CONTAINS NODE")
    return not_contains_node


@tool
def create_is_equals_logic_node(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[DifyState, InjectedState],
    title: str,
    node_id: str,
    value: str,
    context_variable: str
):
    """
    Cria um nó de lógica que verifica se uma variável é igual a um valor específico.

    Parâmetros:
        - title (str): Nome do nó.
        - node_id (str): Identificador único baseado no nome (minúsculas, sem caracteres especiais).
        - value (str): Valor a ser verificado se é igual à variável.
        - context_variable (str): Variável de contexto compartilhada entre nós (exemplo: use "sys.query" para receber o contexto do nó inicial, "<previous_node_id>.text" para receber o contexto de outros nós).
    """
    is_equals_node = create_logic_node(
        title=title,
        node_id=node_id,
        value=value,
        comparison_operator="is",
        context_variable=context_variable
    )

    state["nodes_dicts"].append(is_equals_node)

    print("IS EQUALS NODE")
    return is_equals_node


@tool
def create_not_equals_logic_node(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[DifyState, InjectedState],
    title: str,
    node_id: str,
    value: str,
    context_variable: str
):
    """
    Cria um nó de lógica que verifica se uma variável não é igual a um valor específico.

    Parâmetros:
        - title (str): Nome do nó.
        - node_id (str): Identificador único baseado no nome (minúsculas, sem caracteres especiais).
        - value (str): Valor a ser verificado se não é igual à variável.
        - context_variable (str): Variável de contexto compartilhada entre nós (exemplo: use "sys.query" para receber o contexto do nó inicial, "<previous_node_id>.text" para receber o contexto de outros nós).
    """
    not_equals_node = create_logic_node(
        title=title,
        node_id=node_id,
        value=value,
        comparison_operator="is not",
        context_variable=context_variable
    )

    state["nodes_dicts"].append(not_equals_node)

    print("NOT EQUALS NODE")
    return not_equals_node


@tool
def create_is_empty_logic_node(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[DifyState, InjectedState],
    title: str,
    node_id: str,
    context_variable: str
):
    """
    Cria um nó de lógica que verifica se uma variável está vazia.

    Parâmetros:
        - title (str): Nome do nó.
        - node_id (str): Identificador único baseado no nome (minúsculas, sem caracteres especiais).
        - context_variable (str): Variável de contexto compartilhada entre nós (exemplo: use "sys.query" para receber o contexto do nó inicial, "<previous_node_id>.text" para receber o contexto de outros nós).
    """
    is_empty_node = create_logic_node(
        title=title,
        node_id=node_id,
        value="",
        comparison_operator="empty",
        context_variable=context_variable
    )

    state["nodes_dicts"].append(is_empty_node)

    print("IS EMPTY NODE")
    return is_empty_node


@tool
def create_not_empty_logic_node(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[DifyState, InjectedState],
    title: str,
    node_id: str,
    context_variable: str
):
    """
    Cria um nó de lógica que verifica se uma variável não está vazia.

    Parâmetros:
        - title (str): Nome do nó.
        - node_id (str): Identificador único baseado no nome (minúsculas, sem caracteres especiais).
        - context_variable (str): Variável de contexto compartilhada entre nós (exemplo: use "sys.query" para receber o contexto do nó inicial, "<previous_node_id>.text" para receber o contexto de outros nós).
    """
    not_empty_node = create_logic_node(
        title=title,
        node_id=node_id,
        value="",
        comparison_operator="not empty",
        context_variable=context_variable
    )

    state["nodes_dicts"].append(not_empty_node)

    print("NOT EMPTY NODE")
    return not_empty_node
