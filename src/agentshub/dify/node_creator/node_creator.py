from schema.dify import DifyState
from langgraph.types import Command
from .prompt import NODE_CREATOR
from models.dify import node_creator_dify_model
from tools.dify.ai_tools import create_llm_node
from tools.dify.entry_exit_tools import create_answer_node, create_start_node
from tools.dify.web_tools import create_http_node
from tools.dify.logic_tools import create_contains_logic_node
from langgraph.prebuilt import create_react_agent


# Agente responsável por criar os nodes do sistema
def node_creator(state: DifyState) -> Command:

    tools = [
        create_start_node,
        create_llm_node,
        create_answer_node,
        create_contains_logic_node,
        create_http_node
    ]

    agent = create_react_agent(
        node_creator_dify_model, prompt=NODE_CREATOR, tools=tools
    )

    messages = state["messages"]

    state = {
        "architecture_output": state["architecture_output"],
        "metadata_dict": state["metadata_dict"],
        "nodes_dicts": [],
        "edges_dicts": [],
    }
    response = agent.invoke({'messages': messages, 'state': state})
    print("node_creator executado")
    print("-==-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    print("Response Node Creator")
    print(response)
    print("-==-=-=-=-=-=-=-=-=-=-=-=-=-=-")

    response['active_agent'] = "node_creator"
    response['architecture_output'] = state["architecture_output"]
    response['metadata_dict'] = state['metadata_dict']
    response['nodes_dicts'] = state['nodes_dicts']
    response['edges_dicts'] = state['edges_dicts']

    return Command(update=response)
