from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class AgentState(MessagesState):
    active_agent: str = Field(description="This field should be used to store the active agent in the graph.")
    architecture_output: Optional[Dict] = Field(default=None, description="Stores the architecture output JSON.")