from schema.dify import DifyState
from .prompt import START_NODE_CREATOR
from langgraph.types import Command
from models.dify import start_node_creator_model
from agentshub import only_tools_agent


def start_node_creator(state: DifyState) -> Command:
    return only_tools_agent(start_node_creator_model, START_NODE_CREATOR, state)
