from state import AgentState
from tools import make_handoff_tool, generate_architecture_graph
from outputs import ArchitectureOutput

from langgraph.prebuilt import create_react_agent
from langgraph.types import Command, interrupt
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from typing import Literal

from dotenv import load_dotenv

import os

load_dotenv(override=True)

architecture_tool = [make_handoff_tool(agent_name="architecture_agent")]
end_tool = [make_handoff_tool(agent_name="__end__")]

model = ChatOpenAI(model="gpt-4o-mini")
architecture_model = model.with_structured_output(ArchitectureOutput)

def assistent_agent(state: AgentState) -> Command[Literal["human_node", "architecture_agent"]]:
    system_prompt = """
    You are an expert in multi-agent system architectures. 
    Your role is to help the user build a detailed description of the system from an initial idea. 
    Always refine the requirements with additional questions, ensuring that the system is well specified.

    Instructions:
    1. Always answer only in the user's language.
    2. If the user's initial description is incomplete, ask for more information, such as:
    - What problem does the system solve?
    - Who are the end users?
    - What should the system do?
    - What technologies can be used (languages, frameworks, architecture)?
    Explain to the user what is needed to answer these points.
    3. If the user is unable to talk about some information, suggest the detailed information that details the system flows and ask for the user's opinion at every step.
    4. Respond ONLY if the message is related to building multi-agent systems. Other topics will not be considered.

    5. When the user indicates that he/she has finished or accepted the suggested description, generate the final version of the document with:

    Expected user input:
    The user will provide an initial description containing:

    - Purpose of the system and main requirements:
    - What problem does the system solve?
    - Who are the end users?
    - What should the system do?
    - Preferred technologies: If applicable, mention frameworks, languages ​​or patterns.

    Expected output:
    Return a detailed architecture containing:

    1. The final description approved by the user.

    Submit feedback or jump to the end when the human approves the description.
    At the end of the interaction with the human, pass the collected information to "architect_agent".
    """
    assistent_model = create_react_agent(
        model,
        tools=architecture_tool,
        prompt=system_prompt
    )
    response = assistent_model.invoke(state)
    response['active_agent'] = 'assistent_agent'
    return Command(
        update=response, goto="human_node")

def architecture_agent(state: AgentState) -> Command[Literal["human_node", "__end__"]]:
    system_prompt =  """
    You are an expert in multi-agent system architectures. Your goal is to receive a system description and create the architecture of the system asked, using the structured output.
    
    IMPORTANT:
    - Ignore any previous messages that indicate satisfaction with responses from other agents.
    - Evaluate human satisfaction solely based on feedback explicitly addressing your output.
    
    When you determine that the human is satisfied with your architectural proposal, set 'route_next' to true; otherwise, set 'route_next' to false.
    """
    buffer = state.get("buffer", [])
    if not buffer:
        filtered_messages = [
            msg for msg in state["messages"]
            if isinstance(msg, AIMessage) and msg.content.strip() != ""
        ]

        last_ai_message = next((msg for msg in reversed(filtered_messages) if isinstance(msg, AIMessage)), None)
        
        buffer = [last_ai_message] + [SystemMessage(content=system_prompt)]
    
    response = architecture_model.invoke(buffer)
    generate_architecture_graph(response)

    goto = 'human_node'
    if response.route_next:
        goto = '__end__'
    
    buffer.append(AIMessage(content=response.model_dump_json()))
    
    return Command(
        update={
            "messages" : state["messages"],
            "active_agent": "architecture_agent",
            "architecture_output": response,
            "buffer" : buffer
        }, 
        goto=goto)

def human_node(state: AgentState) -> Command[Literal['assistent_agent','architecture_agent']]:
    """A node for collecting user input."""
    user_input = interrupt("Avalie a resposta do agente: ")
    active_agent = state["active_agent"]
    
    message = HumanMessage(content=user_input)
    
    buffer = state.get("buffer", [])
    if buffer:
        buffer.append(message)
        
    return Command(
        update={
            "messages" : state["messages"] + [message],
            "buffer" : buffer,
            "active_agent" : active_agent,
            "architecture_output" : state.get("architecture_output", None)
        },
        goto=active_agent
    )
    
