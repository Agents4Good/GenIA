from schema.dify import DifyState
from .prompt import LLM_NODE_CREATOR
from langgraph.types import Command
from models.dify import llm_node_creator_model
from agentshub import only_tools_agent


def llm_node_creator(state: DifyState) -> Command:
    return only_tools_agent(llm_node_creator_model, LLM_NODE_CREATOR, state)
