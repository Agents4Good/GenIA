from schema.dify import DifyState
from .prompt import AGENT_NODE_CREATOR
from langgraph.types import Command
from models.dify import agent_node_creator_model
from schema.dify import DifyState
from agentshub import only_tools_agent


def agent_node_creator(state: DifyState) -> Command:
    return only_tools_agent(agent_node_creator_model, AGENT_NODE_CREATOR, state)
