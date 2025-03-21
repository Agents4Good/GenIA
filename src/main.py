from state import AgentState, DifyState
from agents import assistent_agent, architecture_agent, human_node, supervisor_agent, node_creator, edge_creator
from tools import create_llm_node
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage

from utils.io_functions import print_graph

def build_graph():
    tools = [create_llm_node]
    
    tool_node = ToolNode(tools)

    subgraph_builder = StateGraph(DifyState)

    subgraph_builder.add_node("supervisor_agent", supervisor_agent)
    subgraph_builder.add_node("node_creator", node_creator)
    subgraph_builder.add_node("edge_creator", edge_creator)
    subgraph_builder.add_node("tool_node", tool_node)

    subgraph_builder.add_edge(START, "supervisor_agent")
    subgraph_builder.add_edge("node_creator", "tool_node")
    subgraph_builder.add_edge("tool_node", END)
    subgraph = subgraph_builder.compile()

    builder = StateGraph(AgentState)
    
    #Nodes
    builder.add_node("assistent_agent", assistent_agent)
    builder.add_node("human_node", human_node)
    builder.add_node("architecture_agent", architecture_agent)
    builder.add_node("dify", subgraph)

    #Edges
    builder.add_edge(START, "assistent_agent")

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

    
def main():
    graph = build_graph()
    print_graph(graph)
    thread_config = {"configurable": {"thread_id": uuid.uuid4()}}
    human_message = input("Digite sua entrada: ")
    user_input = AgentState(messages=[HumanMessage(content=human_message)])
    num_conversation = 0
    while True:
        print()
        print(f"--- Conversation Turn {num_conversation} ---")
        print()
        if not num_conversation == 0:
            print('Digite "q" para sair')
            human_message = input(f"User: ")
            if(human_message.lower() == 'q'):
                break
            user_input = Command(resume=human_message)
        print()
        for update in graph.stream(
            user_input,
            config=thread_config,
            stream_mode="updates",
        ):
            for node_id, value in update.items():
                if isinstance(value, dict) and value.get("messages", []):
                    last_message = value["messages"][-1]
                    if value.get("active_agent") == "architecture_agent":
                        last_message = value.get('architecture_output')
                        print("=== Arquitetura do Sistema Multiagente ===\n")
                        print("Agentes:")
                        for idx, agent in enumerate(last_message.agents, start=1):
                            print(f"  {idx}. {agent.agent}: {agent.description}")
                        print("\nInterações:")
                        for idx, interaction in enumerate(last_message.interactions, start=1):
                            print(f"  {idx}. {interaction.source} -> {interaction.targets}: {interaction.description}")
                        continue
                    if isinstance(last_message, dict) or last_message.type != "ai":
                        continue
                    print(f"{node_id}: {last_message.content}")
        num_conversation += 1


if __name__ == "__main__":
    main()