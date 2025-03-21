from state import AgentState, DifyState
from tools import make_handoff_tool, sequence_diagram_generator, create_yaml_and_metadata, create_llm_node
from outputs import ArchitectureOutput

from langgraph.prebuilt import create_react_agent
from langgraph.types import Command, interrupt
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from prompts import agents_prompts

from typing import Literal

from dotenv import load_dotenv


load_dotenv(override=True)

architecture_tool = [make_handoff_tool(agent_name="architecture_agent")]
end_tool = [make_handoff_tool(agent_name="__end__")]

model = ChatOpenAI(model="gpt-4o-mini")
architecture_model = model.with_structured_output(ArchitectureOutput)

node_creator_dify_model = model.bind_tools([create_llm_node])

# Agente reponsável por analisar os requisitos do sistema e conversar com o usuário
def assistent_agent(state: AgentState) -> Command[Literal["human_node", "architecture_agent"]]:
    system_prompt = agents_prompts.ASSISTENT_AGENT
    assistent_model = create_react_agent(
        model,
        tools=architecture_tool,
        prompt=system_prompt
    )
    response = assistent_model.invoke(state)
    response['active_agent'] = 'assistent_agent'
    return Command(
        update=response, goto="human_node")


# Agente responsável por criar a arquitetura do sistema com base nos requisitos
def architecture_agent(state: AgentState) -> Command[Literal["human_node", "dify"]]:
    system_prompt =  agents_prompts.ARCHITECTURE_AGENT
    buffer = state.get("buffer", [])
    if not buffer:
        filtered_messages = [
            msg for msg in state["messages"]
            if isinstance(msg, AIMessage) and msg.content.strip() != ""
        ]

        last_ai_message = next((msg for msg in reversed(filtered_messages) if isinstance(msg, AIMessage)), None)
        
        buffer = [last_ai_message] + [SystemMessage(content=system_prompt)]
    
    response = architecture_model.invoke(buffer)
    goto = 'human_node'
    if response.route_next:
        goto = 'dify'
    
    sequence_diagram_generator.invoke(response.model_dump_json())
    
    buffer.append(AIMessage(content=response.model_dump_json()))

    return Command(
        update={
            "messages" : state["messages"],
            "active_agent": "architecture_agent",
            "architecture_output": response,
            "buffer" : buffer
        }, 
        goto=goto)


# Nó que representa a interação do usuário com o sistema
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


# Tool responsável por delegar a criação dos nodes e egdes do sistema
def supervisor_agent(state: AgentState) -> Command[list['node_creator','edge_creator']]:

    create_yaml_and_metadata("Sistema do usuario", 'Sistema do usuario')
    
    novoState = DifyState = {
        "yaml_path": "../output/dify/dify.yml",
        "architecture_output": state["architecture_output"],
        "nodes_code": "",
        "edges_code": ""
    }
    return Command(
        update=novoState,
        goto=["node_creator", "edge_creator"]
    )


# Agente responsável por criar os nodes do sistema
def node_creator(state: DifyState) -> Command[Literal['__end__']]:
    system_prompt = agents_prompts.NODE_CREATOR

    messages = state["messages"] + [system_prompt]
    response = node_creator_dify_model.invoke(messages)
    print(response)
    # tool call para adicionar os nós no YAML
    print("node_creator executado")
    return Command(
        update={
            "messages" : [response]
        },
    )


# Agente responsável por criar as edges do sistema
def edge_creator(state: DifyState) -> Command[Literal['__end__']]:
    system_prompt = agents_prompts.EDGE_CREATOR

    response = "" # llm_call

    # tool call para adicionar os arcos no YAML
    print("edge_creator executado")
    return Command(
    )
