import yaml

from typing import Annotated

from pathlib import Path

from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from utils.plantuml_parser import generate_diagram, json_to_plantuml
from utils.tools_utils import insert_node_yaml, insert_edge_yaml

YAML_PATH = Path("dify.yaml")


def make_handoff_tool(*, agent_name: str):
    """Create a tool that can return handoff via a Command"""
    tool_name = f"transfer_to_{agent_name}"

    @tool(tool_name)
    def handoff_to_agent(
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        """Ask another agent for help."""
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": tool_name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            # navigate to another agent node in the PARENT graph
            goto=agent_name,
            graph=Command.PARENT,
            # This is the state update that the agent `agent_name` will see when it is invoked.
            # We're passing agent's FULL internal message history AND adding a tool message to make sure
            # the resulting chat history is valid.
            update={"messages": state["messages"] + [tool_message]},
        )

    return handoff_to_agent

@tool("sequence_diagram_generator")
def sequence_diagram_generator(architecture_output: str):
    """
    Converte a saída do agente de arquitetura em um diagrama de sequência PlantUML e gera uma imagem do diagrama.
    Retorna o caminho do arquivo gerado.
    """
    plantuml_output = json_to_plantuml(architecture_output)
    diagram_path = generate_diagram(plantuml_output)

def metadata_creator():
    pass


# @tool
def create_yaml_and_metadata(file: Path, name: str, descritption: str):
    """
    Cria um arquivo YAML e insere os metadados a partir de um nome e uma descrição.
    """
    metadata = {
        "app": {
            "description": descritption,
            "mode": "advanced-chat",
            "name": name
        },
        "version": "0.1.5",
        "workflow": {
            "conversation_variables": [],
            "environment_variables": [],
            "graph": {
                "edges": [],
                "nodes": []
            }
        }
    }

    with open(file, "w") as outfile:
        yaml.dump(metadata, outfile, default_flow_style=False, allow_unicode=True)


# @tool
def create_start_node(file: Path, tittle: str, id: str):
    """
    Cria o nó inicial com um título e um id. Esta é a primeira etapa a ser executada no grafo.
    """
    start_node = {
        "id": id,
        "type": "custom",
        "data": {
            "desc": "",
            "title": tittle,
            "type": "start",
            "variables": []
        }
    }

    insert_node_yaml(file, start_node)
    

# @tool
def create_llm_node(file: Path,
                    id: str, 
                    tittle: str, 
                    prompt: str,
                    temperature: float = 0.7,
                    context_variable: str = "",
                    ):
    """
    Cria um nó de LLM.
    """
    llm_node = {
        "id": id,
        "type": "custom",
        "data": {
            "context": {
                "enabled": True,
                "variable_selector": [
                    context_variable.split(".")[0],
                    context_variable.split(".")[1]
                ] if context_variable else []
            },
            "desc": "",
            "model": {
                "completion_params": {
                    "temperature": temperature
                },
                "mode": "chat",
                "name": "gpt-4",
                "provider": "langgenius/openai/openai"
            },
            "prompt_template": [
                {
                    "role": "system",
                    "text": "{{#context#}}\n" + prompt
                }
            ],
            "title": tittle,
            "type": "llm",
            "variables": [],
            "vision": {
                "enabled": False
            }
        }
    }

    insert_node_yaml(file, llm_node)
        

# @tool
def create_answer_node(file: Path, tittle: str, id: str, answer: str):
    """
    Cria um nó de resposta com um título, um id e uma resposta. Esta é a última etapa a ser executada no grafo.
    """
    answer_node = {
        "id": id,
        "type": "custom",
        "data": {
            "answer": answer,
            "desc": "",
            "title": tittle,
            "type": "answer",
            "variables": []
        }
    }

    insert_node_yaml(file, answer_node)


# @tool
def create_edges(file: Path, id: str, source: str, target: str):
    """
    Cria uma edge entre dois nós.
    """
    edge = {
        "id": id,
        "source": source,
        "target": target,
        "type": "custom"
    }

    insert_edge_yaml(file, edge)
    

create_yaml_and_metadata(YAML_PATH,
                         "Contador de piadas",
                         "Um contador de piadas que conta piadas engraçadas.")

create_start_node(YAML_PATH, "Início", "start")

create_llm_node(YAML_PATH,
                "llm1",
                "Criador de Perguntas",
                """Seu trabalho é gerar o início de uma piada que mais tarde será encaminhada para outro agente que a completará\nO tema da piada será passado pelo usuário como entrada.\nAs piadas devem ser estruturadas em forma de pergunta, por exemplo:\n"O que é um ponto preto em cima do castelo?""",
                1.0,
                "sys.query")

create_llm_node(YAML_PATH,
                "llm2",
                "Criador de respostas",
                """Seu trabalho é receber um início de piada em forma de pergunta e respondê-la de forma engraçada e que faça sentido com o tópico abordado.""",
                1.0,
                "llm1.text"
                )

create_answer_node(YAML_PATH,
                   "Fim",
                   "end",
                   """{{#llm1.text#}}\n{{#llm2.text#}}""")

create_edges(YAML_PATH, "edge1", "start", "llm1")
create_edges(YAML_PATH, "edge2", "llm1", "llm2")
create_edges(YAML_PATH, "edge3", "llm2", "end")