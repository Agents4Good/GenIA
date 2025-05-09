from schema.dify import DifyState
from .prompt import HTTP_NODE_CREATOR
from langgraph.types import Command
from models.dify import http_node_creator_model
from agentshub import only_tools_agent


def http_node_creator(state: DifyState) -> Command:
    return only_tools_agent(http_node_creator_model, HTTP_NODE_CREATOR, state)
