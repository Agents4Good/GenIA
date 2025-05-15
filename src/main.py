from schema.genia import AgentState
from schema.dify import DifyState
from agentshub.genia import (
    requirements_engineer,
    architect,
    human_node,
)
from agentshub.dify import (
    supervisor,
    start_node_creator,
    llm_node_creator,
    http_node_creator,
    logic_node_creator,
    answer_node_creator,
    agent_node_creator,
    edge_creator
)

from utils.dify import (
    dify_yaml_builder,
    call_dify_tools
)

import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from utils.genia.io_functions import print_graph


dify_agents = ["start_node_creator", "llm_node_creator",
               "logic_node_creator", "http_node_creator", "agent_node_creator",
               "answer_node_creator"]


def supervisor_conditional_edge(state: DifyState):
    print("=============================\nconditional_edge")
    agents = state["messages"][-1].content.split(", ")
    print(agents)
    print("=============================")
    return agents


def build_graph():
    subgraph_builder = StateGraph(DifyState)

    subgraph_builder.add_node("supervisor_agent", supervisor)
    subgraph_builder.add_node("edge_creator", edge_creator)
    subgraph_builder.add_node("tools_node_creator", call_dify_tools)
    subgraph_builder.add_node("tools_edge_creator", call_dify_tools)
    subgraph_builder.add_node("dify_yaml_builder", dify_yaml_builder)
    subgraph_builder.add_node("start_node_creator", start_node_creator)
    subgraph_builder.add_node("llm_node_creator", llm_node_creator)
    subgraph_builder.add_node("logic_node_creator", logic_node_creator)
    subgraph_builder.add_node("http_node_creator", http_node_creator)
    subgraph_builder.add_node("agent_node_creator", agent_node_creator)
    subgraph_builder.add_node("answer_node_creator", answer_node_creator)

    dify_agents_map = {agent: agent for agent in dify_agents}
    subgraph_builder.add_edge(START, "supervisor_agent")
    subgraph_builder.add_conditional_edges(
        "supervisor_agent", supervisor_conditional_edge, dify_agents_map)
    subgraph_builder.add_edge("start_node_creator", "tools_node_creator")
    subgraph_builder.add_edge("llm_node_creator", "tools_node_creator")
    subgraph_builder.add_edge("logic_node_creator", "tools_node_creator")
    subgraph_builder.add_edge("http_node_creator", "tools_node_creator")
    subgraph_builder.add_edge("agent_node_creator", "tools_node_creator")
    subgraph_builder.add_edge("answer_node_creator", "tools_node_creator")
    subgraph_builder.add_edge("tools_node_creator", "edge_creator")
    subgraph_builder.add_edge("edge_creator", "tools_edge_creator")
    subgraph_builder.add_edge("tools_edge_creator", "dify_yaml_builder")
    subgraph_builder.add_edge("dify_yaml_builder", END)
    subgraph = subgraph_builder.compile()

    builder = StateGraph(AgentState)

    # Nodes
    builder.add_node("requirements_engineer", requirements_engineer)
    builder.add_node("human_node", human_node)
    builder.add_node("architecture_agent", architect)
    builder.add_node("dify", subgraph)

    # Edges
    builder.add_edge(START, "requirements_engineer")

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


def print_architecture(last_message):
    """Imprime a arquitetura do sistema multiagente."""
    print("\n=== Arquitetura do Sistema Multiagente ===\n")
    print("Nós:")

    for idx, node in enumerate(last_message.nodes, start=1):
        print(f"  {idx}. {node.node}: {node.description}")

    print("\nInterações:")
    for idx, interaction in enumerate(last_message.interactions, start=1):
        print(
            f"  {idx}. {interaction.source} -> {interaction.targets}: {interaction.description}"
        )


def main():

    graph = build_graph()
    # print_graph(graph)
    thread_config = {"configurable": {"thread_id": uuid.uuid4()}}
    num_conversation = 0

    human_message = input("Digite sua entrada: ")
    user_input = AgentState(messages=[HumanMessage(content=human_message)])

    while True:
        print(f"\n--- Conversation Turn {num_conversation} ---\n")

        if num_conversation > 0:
            print('Digite "q" para sair')
            human_message = input("User: ")
            if human_message.lower() == "q":
                break
            user_input = Command(resume=human_message)

        final_state = None

        for update in graph.stream(
            user_input, config=thread_config, stream_mode="updates"
        ):
            for node_id, value in update.items():
                if isinstance(value, dict) and value.get("messages", []):
                    last_message = value["messages"][-1]

                    if not isinstance(last_message, dict) and last_message.type == "ai":
                        print(f"\n {node_id}: {last_message.content}")

                    final_state = value

        if final_state:
            architecture_output = final_state.get("architecture_output")
            if architecture_output:
                print_architecture(architecture_output)

        num_conversation += 1


if __name__ == "__main__":
    main()
