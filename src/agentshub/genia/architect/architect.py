from schema.genia import AgentState
from .prompt import ARCHITECT_AGENT
from langgraph.types import Command
from typing import Literal
from langchain_core.messages import SystemMessage, AIMessage
from models.genia import architecture_model
from models import model
from .utils import extract_json
from tools.genia.utils import sequence_diagram_generator


# Agente responsável por criar a arquitetura do sistema com base nos requisitos
def architect(state: AgentState) -> Command[Literal["human_node", "dify"]]:
    system_prompt = ARCHITECT_AGENT
    buffer = state.get("buffer", [])
    if not buffer:
        filtered_messages = [
            msg
            for msg in state["messages"]
            if isinstance(msg, AIMessage) and msg.content.strip() != ""
        ]

        last_ai_message = next(
            (msg for msg in reversed(filtered_messages) if isinstance(msg, AIMessage)),
            None,
        )

        print("============================================================")
        print(last_ai_message)
        print("============================================================")

        buffer = [SystemMessage(content=system_prompt).content] + [last_ai_message.content]

    print("============================================================")
    print(buffer)
    print("============================================================")

    response = architecture_model.invoke(buffer)

    print("============================================================")
    print(response)
    print("============================================================")

    response = extract_json(response.content)

    goto = "human_node"
    if response.route_next:
        goto = "dify"

    sequence_diagram_generator.invoke(response.model_dump_json())

    buffer.append(AIMessage(content=response.model_dump_json()))

    return Command(
        update={
            "messages": state["messages"],
            "active_agent": "architecture_agent",
            "architecture_output": response,
            "buffer": buffer,
        },
        goto=goto,
    )
