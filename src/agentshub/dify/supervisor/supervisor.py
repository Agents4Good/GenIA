from schema.dify import DifyState
from schema.genia import AgentState
from langgraph.types import Command
from tools.dify import create_yaml_metadata


# Tool responsável por delegar a criação dos nodes e egdes do sistema
def supervisor(state: AgentState) -> Command:
    yaml_metadata = create_yaml_metadata("Sistema do usuario", " ")
    novoState = DifyState(
        architecture_output=state["architecture_output"], metadata_dict=yaml_metadata, nodes_dicts=[], edges_dicts=[],
    )
    return Command(update=novoState, goto=["node_creator"])
