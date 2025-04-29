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
        node_creator_dify_model, prompt=NODE_CREATOR, tools= tools
    )

    messages = state["messages"]

    response = agent.invoke({'messages':messages,'nodes_dicts':[]},debug=True)
    print("node_creator executado")
    print(response)
    return Command(update={"messages": [response]})
