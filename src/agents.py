from state import AgentState
from tools import make_handoff_tool

from langgraph.types import Command, interrupt
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from typing import Literal

from dotenv import load_dotenv

import os

load_dotenv(override=True)
model = ChatOpenAI(model="gpt-4-turbo")

def assistent_agent(state: AgentState) -> Command[Literal["human_node", "architect_agent"]]:
    system_prompt = """
    Instruction:
    You are an expert in multi-agent system architectures. Based on the user's input, identify if there is any missing information and ask for clarification in a simple and objective way.
    REPLY ONLY IN THE USER'S LANGUAGE.
    ONLY!!!! respond if the message is related to the generation of multi-agent systems. Other topics will not be considered.
    Move to the end when the human says he/she is done with the conversation.

    Input:
    The user will provide a description including:
    - System goal: What the system should solve or optimize.
    - Environment: Where the system operates and any constraints.
    - Preferred technologies: If applicable, mention frameworks, languages ​​or patterns.

    Expected output:
    You should return the information provided by the user, organized into topics:
    1. System goal: What the system should solve or optimize.
    2. Environment: Where the system operates and any constraints.
    3. Preferred technologies: If applicable, mention frameworks, languages ​​or patterns.

    At the end of the interaction with the human, pass the collected information to "architect_agent" writing an "#architect_agent" code in the end.
    """
    messages = state["messages"] + [SystemMessage(content=system_prompt)]
    response = model.invoke(messages)
    
    messages.append(response)
    if "#architect_agent" in response.content:
        return Command(
            update={
                "messages" : messages,
                "active_agent" : "architect_agent"
            }, goto="human_node")
    return Command(
        update={
                "messages" : messages,
                "active_agent" : "assistent_agent"
            }, goto="human_node")

def architect_agent(state: AgentState) -> Command[Literal["human_node", "__end__"]]:
    system_prompt = """
    Instruction:
    You are a multi-agent system architect. Based on the user's input, design a multi-agent system that meets the user's needs. 
    You must return a description of the multi-agent system, including:
    - Agents: The roles of each agent in the system.
    - Communication: The communication protocol between agents.
    """
    
    messages = state["messages"] + [SystemMessage(content=system_prompt)]
    response = model.invoke(messages)
    
    messages.append(response)
    return Command(
        update={
                "messages" : messages,
                "active_agent" : "architect_agent"
            }, goto="human_node")

def human_node(state: AgentState) -> Command[Literal['assistent_agent', 'architect_agent']]:
    """A node for collecting user input."""
    user_input = interrupt("Avalie a resposta do agente: ")
    active_agent = state["active_agent"]
    
    return Command(
        update={
            "messages" : [HumanMessage(content=user_input)]
        },
        goto=active_agent
    )