from schema.dify import DifyState
from .prompt import LOGIC_NODE_CREATOR
from langgraph.types import Command
from models.dify import logic_node_creator_model
from agentshub import only_tools_agent


def logic_node_creator(state: DifyState) -> Command:
    return only_tools_agent(logic_node_creator_model, LOGIC_NODE_CREATOR, state)
