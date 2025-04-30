from schema.dify import DifyState
from langgraph.types import Command
from .prompt import EDGE_CREATOR
from models.dify import edge_creator_dify_model
from tools.dify import create_edges,create_logic_edges
from langgraph.prebuilt import create_react_agent

# Agente responsável por criar as edges do sistema
def edge_creator(state: DifyState) -> Command:

    tools = [
        create_logic_edges,
        create_edges
    ]

    agent = create_react_agent(
        edge_creator_dify_model, prompt=EDGE_CREATOR, tools=tools
    )
    state = {
        "architecture_output": state["architecture_output"],
        "metadata_dict": state["metadata_dict"],
        "nodes_dicts": state['nodes_dicts'],
        "edges_dicts": [],
    }
    print("-==-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    messages = state["messages"]
    response = agent.invoke({'messages':messages, 'state':state})
    print("edge_creator executado")
    print("-==-=-=-=-=-=-=-=-=-=-=-=-=-=-")


    response['active_agent'] = "edge_creator"
    response['architecture_output'] = state["architecture_output"]
    response['metadata_dict'] = state['metadata_dict']
    response['nodes_dicts'] = state['nodes_dicts']
    response['edges_dicts'] = state['edges_dicts']

    print("edge_creator executado")
    return Command(
        update=response
    )
