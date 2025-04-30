import yaml
from schema.dify import DifyState
from langgraph.types import Command
from langchain_core.messages import SystemMessage
from typing import List
from pathlib import Path
from utils.genia import get_generated_files_path
from tools.dify import (
    create_llm_node,
    create_answer_node,
    create_start_node,
    create_contains_logic_node,
    create_edges,
    create_logic_edges,
    create_http_node,
)
from utils.dify import dify_import_yaml

YAML_PATH = get_generated_files_path("dify.yaml")


def _write_dify_yaml(state: DifyState):
    yaml_dify = state["metadata_dict"]
    yaml_dify["workflow"]["graph"]["nodes"].extend(state["nodes_dicts"])
    yaml_dify["workflow"]["graph"]["edges"].extend(state["edges_dicts"])

    file = Path(YAML_PATH)
    with open(file, "w") as outfile:
        yaml.dump(yaml_dify, outfile,
                  default_flow_style=False, allow_unicode=True)


def dify_yaml_builder(state: DifyState) -> Command:
    _write_dify_yaml(state)
    try:
        dify_import_yaml("dify.yaml", "local")
    except Exception as e:
        print(
            "Não foi possível importar o yaml para o app Dify local, tentando importar na web"
        )
        try:
            dify_import_yaml("dify.yaml", "web")
        except Exception as e:
            print(e)
            print("Não foi possível importar o yaml para o app Dify local")

    return Command(
        update={
            "messages": [SystemMessage(content="Successfully create the dify yaml")]
        },
    )


tools_dify = {
    "create_llm_node": create_llm_node,
    "create_answer_node": create_answer_node,
    "create_start_node": create_start_node,
    # "create_start_with_logic_node": create_start_with_logic_node,
    # "create_end_with_logic_node": create_end_with_logic_node,
    "create_contains_logic_node": create_contains_logic_node,
    # "create_not_contains_logic_node": create_not_contains_logic_node,
    # "create_is_equals_logic_node": create_is_equals_logic_node,
    # "create_not_equals_logic_node": create_not_equals_logic_node,
    # "create_is_empty_logic_node": create_is_empty_logic_node,
    # "create_not_empty_logic_node": create_not_empty_logic_node,
    "create_edges": create_edges,
    "create_logic_edges": create_logic_edges,
    "create_http_node": create_http_node,
}


def call_dify_tools(state: DifyState) -> List[Command]:
    tool_calls = state["messages"][-1].tool_calls
    print(tool_calls)
    commands = []
    for tool_call in tool_calls:
        commands.append(tools_dify[tool_call["name"]].invoke(tool_call))

    return commands
