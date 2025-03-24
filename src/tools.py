from typing import Annotated, Literal

from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
import networkx as nx
import matplotlib.pyplot as plt
import textwrap

def make_handoff_tool(*, agent_name: str):
    """Create a tool that can return handoff via a Command"""
    tool_name = f"transfer_to_{agent_name}"

    @tool(tool_name)
    def handoff_to_agent(
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        """Ask another agent for help."""
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": tool_name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            # navigate to another agent node in the PARENT graph
            goto=agent_name,
            graph=Command.PARENT,
            # This is the state update that the agent `agent_name` will see when it is invoked.
            # We're passing agent's FULL internal message history AND adding a tool message to make sure
            # the resulting chat history is valid.
            update={"messages": state["messages"] + [tool_message]},
        )

    return handoff_to_agent

def generate_architecture_graph(architecture_output):
    G = nx.DiGraph()

    for agent in architecture_output.agents:
        G.add_node(agent.agent, description=agent.description)

    for interaction in architecture_output.interactions:
        G.add_edge(interaction.source, interaction.targets, description=interaction.description)

    visualize_graph(G)

def visualize_graph(G: nx.DiGraph):
    pos = nx.spring_layout(G, seed=42)  # Keeps positions fixed for consistency
    plt.figure(figsize=(12, 8))

    # Draw nodes with specified colors and sizes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000, edgecolors='black')

    # Draw edges with arrows
    for (u, v, d) in G.edges(data=True):
        # Check if there is a reverse edge to adjust curvature
        rad = 0.2 if G.has_edge(v, u) else 0
        # Ensure arrows are drawn with the correct style
        nx.draw_networkx_edges(
            G, pos, edgelist=[(u, v)], edge_color='gray',
            arrows=True, arrowstyle='-|>', connectionstyle=f"arc3,rad={rad}"
        )

    # Add labels to nodes
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

    # Improve edge label display
    edge_labels = nx.get_edge_attributes(G, 'description')
    
    # Adjust labels for bidirectional edges
    adjusted_labels = {}
    for (u, v), text in edge_labels.items():
        wrapped_text = "\n".join(textwrap.wrap(text, width=30))
        rad = 0.2 if (v, u) in edge_labels else 0
        adjusted_labels[(u, v)] = (wrapped_text, rad)

    # Plot adjusted edge labels
    for (u, v), (label, rad) in adjusted_labels.items():
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels={(u, v): label},
            font_color='red', font_size=9, label_pos=0.5, rotate=False,
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
        )

    plt.title('Arquitetura do Sistema Multiagente', fontsize=14)
    plt.axis('off')
    plt.savefig("grafo_da_arquitetura.png")
