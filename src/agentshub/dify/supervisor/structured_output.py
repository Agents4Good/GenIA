from pydantic import BaseModel, Field
from typing import List


class SupervisorOutput(BaseModel):
    """
    Represents the Dify's agents that will be run.
    """
    agents: List[str] = Field(description="List of Dify's agents")