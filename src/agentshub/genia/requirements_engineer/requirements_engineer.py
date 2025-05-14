from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from .prompt import REQUIREMENTS_ENGINEER, REQUIREMENTS_ENGINEER_REFACTED
from typing import Literal
from schema.genia import AgentState
from models import model
from tools.genia import make_handoff_tool


requirements_engineer_tool = [make_handoff_tool(agent_name="architecture_agent")]


# Agente reponsável por analisar os requisitos do sistema e conversar com o usuário
def requirements_engineer(
    state: AgentState, 
    max_retries: int = 3,
) -> Command[Literal["human_node", "architecture_agent"]]:
    system_prompt = REQUIREMENTS_ENGINEER_REFACTED
    requirements_engineer_model = create_react_agent(
        model, tools=requirements_engineer_tool, prompt=system_prompt
    )
    
    for attempt in range(max_retries):
        try:
            response = requirements_engineer_model.invoke(state)
            if isinstance(response['messages'][-2],ToolMessage):
                
                return Command(update=response,goto='architecture_agent')
            
            response["active_agent"] = "requirements_engineer"
            return Command(update=response, goto="human_node")

        except Exception as e:
            if attempt == max_retries - 1:
                print(f'Falha após várias tentativas. Error: {e}')
                return Command(update=state, goto="human_node")