from schema.dify import DifyState
from langgraph.types import Command
from langchain_core.messages import SystemMessage
from models.dify import agent_node_creator_model
from schema.dify import DifyState
from langchain_core.language_models.chat_models import BaseChatModel
from utils import content_to_tool


def only_tools_agent(model: BaseChatModel, prompt: str, state: DifyState) -> Command:
    messages = state["messages"] + [SystemMessage(prompt)]
    response = model.invoke(messages)

    if response.content:
        response = content_to_tool(response)

    return Command(
        update={"messages": [response]}
    )
