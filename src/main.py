from schema.genia import AgentState
from schema.dify import DifyState
from agentshub.genia import (
    requirements_engineer,
    architect,
    human_node,
)

from agentshub.dify import (
    supervisor,
    node_creator,
    edge_creator
)

from utils.dify import (
    dify_yaml_builder,
    call_dify_tools
)

from tools.dify import (
    create_llm_node,
    create_answer_node,
    create_start_node,
    create_contains_logic_node,
    create_edges,
    create_logic_edges,
    create_http_node
)

import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from utils.genia.io_functions import print_graph


def build_graph():
    subgraph_builder = StateGraph(DifyState)
    tools_dify = [create_llm_node,
    create_answer_node,
    create_start_node,
    create_contains_logic_node,
    create_edges,
    create_logic_edges,
    create_http_node]
    tool_node = ToolNode(tools_dify)

    subgraph_builder.add_node("supervisor_agent", supervisor)
    subgraph_builder.add_node("node_creator", node_creator)
    subgraph_builder.add_node("edge_creator", edge_creator)
    subgraph_builder.add_node("tools_node_creator", tool_node)
    subgraph_builder.add_node("tools_edge_creator", tool_node)
    subgraph_builder.add_node("dify_yaml_builder", dify_yaml_builder)

    subgraph_builder.add_edge(START, "supervisor_agent")
    subgraph_builder.add_edge("supervisor_agent", "node_creator")
    subgraph_builder.add_edge("node_creator", "tools_node_creator")
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
    print("Agentes:")

    for idx, agent in enumerate(last_message.agents, start=1):
        print(f"  {idx}. {agent.agent}: {agent.description}")

    print("\nInterações:")
    for idx, interaction in enumerate(last_message.interactions, start=1):
        print(
            f"  {idx}. {interaction.source} -> {interaction.targets}: {interaction.description}"
        )


def main():
    graph = build_graph()
    print_graph(graph)
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

        printed_architecture = False

        for update in graph.stream(
            user_input, config=thread_config, stream_mode="updates"
        ):
            for node_id, value in update.items():
                if isinstance(value, dict) and value.get("messages", []):
                    last_message = value["messages"][-1]

                    if (
                        value.get("active_agent") == "architecture_agent"
                        and not printed_architecture
                    ):
                        print_architecture(value.get("architecture_output"))
                        printed_architecture = True
                        continue

                    if not isinstance(last_message, dict) and last_message.type == "ai":
                        print(f"{node_id}: {last_message.content}")

        num_conversation += 1


if __name__ == "__main__":
    main()
