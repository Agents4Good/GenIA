from typing import Annotated

from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.prebuilt import InjectedState
from schema.dify import DifyState

LLAMA = ["claude-3-haiku-20240307", "langgenius/anthropic/anthropic"]
OPENAI = ["gpt-4", "langgenius/openai/openai"]


@tool
def create_llm_node(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[DifyState, InjectedState],
    title: str,
    node_id: str,
    role: str,
    context_variable: str,
    task: str,
    temperature: float,
):
    """
    Cria um nó de agente (LLM) para um workflow multiagente.

    Parâmetros:
        - title (str): Nome do nó.
        - node_id (str): Identificador único baseado no nome (minúsculas, sem caracteres especiais).
        - role (str): Papel do agente no workflow (exemplo: "Você é um especialista em contar piadas").
        - context_variable (str): Variável de contexto compartilhada entre nós (exemplo: use "sys.query" para receber o contexto do nó inicial, "<previous_node_id>.text" para receber o contexto de outros nós).
        - task (str): O que o agente faz.
        - temperature (float): Criatividade do modelo, entre 0 e 1.
    """
    llm_node = {
        "id": node_id,
        "type": "custom",
        "data": {
            "context": {
                "enabled": True,
                "variable_selector": [
                    context_variable.split(".")[0],
                    context_variable.split(".")[1],
                ]
                if context_variable
                else [],
            },
            "desc": "",
            "model": {
                "completion_params": {"temperature": temperature},
                "mode": "chat",
                "name": LLAMA[0],
                "provider": LLAMA[1],
            },
            "prompt_template": [
                {"role": "system", "text": f"""{role}\n{task}"""},
                {"role": "user", "text": "{{#context#}}"}
            ],
            "title": title,
            "type": "llm",
            "variables": [],
            "vision": {"enabled": False},
        },
    }

    state["nodes_dicts"].append(llm_node)
    print("LLM NODE")
    return llm_node
